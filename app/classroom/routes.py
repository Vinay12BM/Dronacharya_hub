import os
import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from app.models import Classroom, ClassroomMember, ClassroomPost, ClassroomAssignment, AssignmentSubmission, User

classroom_bp = Blueprint('classroom', __name__, template_folder='../../templates/classroom')

@classroom_bp.route('/')
@login_required
def index():
    # User's classrooms (both taught and enrolled)
    taught = Classroom.query.filter_by(instructor_id=current_user.id).all()
    enrolled_memberships = ClassroomMember.query.filter_by(user_id=current_user.id).all()
    enrolled = [m.classroom_parent for m in enrolled_memberships]
    
    return render_template('classroom/index.html', taught=taught, enrolled=enrolled)

@classroom_bp.route('/create', methods=['POST'])
@login_required
def create():
    name = request.form.get('name')
    description = request.form.get('description', '')
    if name:
        join_code = str(uuid.uuid4())[:8].upper()
        new_class = Classroom(
            name=name,
            description=description,
            join_code=join_code,
            instructor_id=current_user.id
        )
        db.session.add(new_class)
        db.session.commit()
        flash('Classroom created successfully!', 'success')
    else:
        flash('Classroom name is required.', 'danger')
    return redirect(url_for('classroom.index'))

@classroom_bp.route('/join', methods=['POST'])
@login_required
def join():
    code = request.form.get('code')
    if code:
        classroom = Classroom.query.filter_by(join_code=code).first()
        if classroom:
            if classroom.instructor_id == current_user.id:
                flash("You are the instructor of this class.", "info")
            else:
                existing = ClassroomMember.query.filter_by(classroom_id=classroom.id, user_id=current_user.id).first()
                if not existing:
                    new_member = ClassroomMember(classroom_id=classroom.id, user_id=current_user.id, role='student')
                    db.session.add(new_member)
                    db.session.commit()
                    flash(f'Successfully joined {classroom.name}', 'success')
                else:
                    flash('You are already a member of this classroom.', 'info')
        else:
            flash('Invalid class code.', 'danger')
    return redirect(url_for('classroom.index'))

@classroom_bp.route('/<int:id>/stream')
@login_required
def stream(id):
    classroom = Classroom.query.get_or_404(id)
    # Validate membership
    is_instructor = (classroom.instructor_id == current_user.id)
    is_member = ClassroomMember.query.filter_by(classroom_id=id, user_id=current_user.id).first()
    if not is_instructor and not is_member:
        flash('Access denied.', 'danger')
        return redirect(url_for('classroom.index'))
    
    posts = ClassroomPost.query.filter_by(classroom_id=id).order_by(ClassroomPost.created_at.desc()).all()
    return render_template('classroom/stream.html', classroom=classroom, posts=posts, is_instructor=is_instructor)

@classroom_bp.route('/<int:id>/post', methods=['POST'])
@login_required
def create_post(id):
    classroom = Classroom.query.get_or_404(id)
    is_instructor = (classroom.instructor_id == current_user.id)
    is_member = ClassroomMember.query.filter_by(classroom_id=id, user_id=current_user.id).first()
    if not is_instructor and not is_member:
        return redirect(url_for('classroom.index'))
        
    content = request.form.get('content')
    if content:
        new_post = ClassroomPost(classroom_id=id, author_id=current_user.id, content=content)
        db.session.add(new_post)
        db.session.commit()
        flash('Post added.', 'success')
    return redirect(url_for('classroom.stream', id=id))

@classroom_bp.route('/<int:id>/classwork')
@login_required
def classwork(id):
    classroom = Classroom.query.get_or_404(id)
    is_instructor = (classroom.instructor_id == current_user.id)
    is_member = ClassroomMember.query.filter_by(classroom_id=id, user_id=current_user.id).first()
    if not is_instructor and not is_member:
        return redirect(url_for('classroom.index'))
        
    assignments = ClassroomAssignment.query.filter_by(classroom_id=id).order_by(ClassroomAssignment.created_at.desc()).all()
    return render_template('classroom/classwork.html', classroom=classroom, assignments=assignments, is_instructor=is_instructor)

@classroom_bp.route('/<int:id>/classwork/create', methods=['POST'])
@login_required
def create_assignment(id):
    classroom = Classroom.query.get_or_404(id)
    if classroom.instructor_id != current_user.id:
        flash('Only instructors can create assignments.', 'danger')
        return redirect(url_for('classroom.classwork', id=id))
        
    title = request.form.get('title')
    description = request.form.get('description', '')
    due_date_str = request.form.get('due_date')
    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            pass

    if title:
        assignment = ClassroomAssignment(
            classroom_id=id,
            title=title,
            description=description,
            due_date=due_date
        )
        db.session.add(assignment)
        db.session.commit()
        flash('Assignment created.', 'success')
    return redirect(url_for('classroom.classwork', id=id))

@classroom_bp.route('/assignment/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
def assignment_detail(assignment_id):
    assignment = ClassroomAssignment.query.get_or_404(assignment_id)
    classroom = assignment.classroom_parent
    is_instructor = (classroom.instructor_id == current_user.id)
    is_member = ClassroomMember.query.filter_by(classroom_id=classroom.id, user_id=current_user.id).first()
    
    if not is_instructor and not is_member:
        return redirect(url_for('classroom.index'))

    if request.method == 'POST' and not is_instructor:
        text_content = request.form.get('text_content', '')
        file = request.files.get('file')
        file_path = None
        
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(save_path)
            file_path = f"uploads/{unique_filename}"
            
        submission = AssignmentSubmission.query.filter_by(assignment_id=assignment.id, student_id=current_user.id).first()
        if not submission:
            submission = AssignmentSubmission(
                assignment_id=assignment.id,
                student_id=current_user.id,
                text_content=text_content,
                file_path=file_path
            )
            db.session.add(submission)
        else:
            submission.text_content = text_content
            submission.submitted_at = datetime.utcnow()
            if file_path:
                submission.file_path = file_path
                
        db.session.commit()
        flash('Assignment submitted.', 'success')
        return redirect(url_for('classroom.assignment_detail', assignment_id=assignment_id))

    if is_instructor:
        submissions = AssignmentSubmission.query.filter_by(assignment_id=assignment.id).all()
        return render_template('classroom/assignment_instructor.html', classroom=classroom, assignment=assignment, submissions=submissions)
    else:
        submission = AssignmentSubmission.query.filter_by(assignment_id=assignment.id, student_id=current_user.id).first()
        return render_template('classroom/assignment_student.html', classroom=classroom, assignment=assignment, submission=submission)

@classroom_bp.route('/assignment/grade/<int:submission_id>', methods=['POST'])
@login_required
def grade_submission(submission_id):
    submission = AssignmentSubmission.query.get_or_404(submission_id)
    assignment = submission.assignment_parent
    classroom = assignment.classroom_parent
    
    if classroom.instructor_id != current_user.id:
        return redirect(url_for('classroom.index'))
        
    grade = request.form.get('grade')
    feedback = request.form.get('feedback', '')
    
    submission.grade = grade
    submission.feedback = feedback
    db.session.commit()
    flash('Grade saved.', 'success')
    return redirect(url_for('classroom.assignment_detail', assignment_id=assignment.id))

@classroom_bp.route('/<int:id>/people')
@login_required
def people(id):
    classroom = Classroom.query.get_or_404(id)
    is_instructor = (classroom.instructor_id == current_user.id)
    is_member = ClassroomMember.query.filter_by(classroom_id=id, user_id=current_user.id).first()
    if not is_instructor and not is_member:
        return redirect(url_for('classroom.index'))
        
    members = ClassroomMember.query.filter_by(classroom_id=id).all()
    return render_template('classroom/people.html', classroom=classroom, members=members, is_instructor=is_instructor)
