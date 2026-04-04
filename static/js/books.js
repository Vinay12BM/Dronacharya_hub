// ── SELLER GPS PICKER (list_book page) ──────────────────────────
let sellerMap, sellerMarker;

function getSellerLocation() {
  const btn = document.getElementById('location-btn');
  const status = document.getElementById('location-status');
  btn.disabled = true;
  btn.innerHTML = '⏳ Detecting...';
  if (!navigator.geolocation) { alert('GPS not supported.'); btn.disabled=false; return; }
  navigator.geolocation.getCurrentPosition(
    pos => {
      const lat = pos.coords.latitude, lon = pos.coords.longitude;
      document.getElementById('lat-input').value  = lat;
      document.getElementById('lon-input').value  = lon;
      btn.innerHTML = '✅ Location Detected';
      btn.style.background = '#2D6A4F';
      btn.disabled = false;
      status.textContent = '✅ Location found! Drag the pin to fine-tune.';
      status.className = 'text-sm p-3 rounded-xl bg-green-50 text-green-700 mb-3';
      status.classList.remove('hidden');
      reverseGeocode(lat, lon);
      initSellerMap(lat, lon);
    },
    err => {
      btn.disabled=false;
      btn.innerHTML='📍 Try Again';
      status.textContent = '❌ Allow location access and try again.';
      status.className = 'text-sm p-3 rounded-xl bg-red-50 text-red-700 mb-3';
      status.classList.remove('hidden');
    },
    { enableHighAccuracy:true, timeout:10000 }
  );
}

function reverseGeocode(lat, lon) {
  fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&zoom=16`, {
    headers:{'Accept-Language':'en','User-Agent':'DronacharyaHub/1.0'}
  }).then(r=>r.json()).then(d=>{
    const addr = d.display_name || `${lat.toFixed(4)},${lon.toFixed(4)}`;
    document.getElementById('addr-input').value = addr;
    const disp = document.getElementById('address-display');
    if(disp){ document.getElementById('address-text').textContent=addr; disp.classList.remove('hidden'); }
  }).catch(()=>{ document.getElementById('addr-input').value=`${lat.toFixed(4)},${lon.toFixed(4)}`; });
}

function initSellerMap(lat, lon) {
  document.getElementById('seller-map').classList.remove('hidden');
  document.getElementById('map-hint')?.classList.remove('hidden');
  if(sellerMap){ sellerMap.remove(); sellerMap=null; }
  sellerMap = L.map('seller-map').setView([lat,lon],16);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'© OpenStreetMap'}).addTo(sellerMap);
  const icon = L.divIcon({html:'<div style="background:#1B4332;color:white;border-radius:50%;width:40px;height:40px;display:flex;align-items:center;justify-content:center;font-size:20px;border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.4)">📚</div>',className:'',iconSize:[40,40],iconAnchor:[20,20]});
  sellerMarker = L.marker([lat,lon],{draggable:true,icon}).addTo(sellerMap);
  sellerMarker.bindPopup('📌 Drag to fine-tune your location').openPopup();
  sellerMarker.on('dragend',e=>{
    const ll=e.target.getLatLng();
    document.getElementById('lat-input').value=ll.lat;
    document.getElementById('lon-input').value=ll.lng;
    reverseGeocode(ll.lat,ll.lng);
  });
}

// ── NEARBY BOOK MAP (index/browse pages) ────────────────────────
let nearbyMap, nearbyMarkers=[], userLat, userLon;

function findNearbyBooks() {
  const target = document.getElementById('nearby-section');
  if(target) {
    target.classList.remove('hidden');
    target.scrollIntoView({behavior:'smooth'});
  }
  if(!navigator.geolocation){ alert('GPS not supported.'); return; }
  const status = document.getElementById('nearby-status');
  if(status) status.textContent='🔍 Detecting your location...';
  navigator.geolocation.getCurrentPosition(
    pos=>{
      userLat=pos.coords.latitude; userLon=pos.coords.longitude;
      if(status) status.textContent='✅ Showing books near you!';
      initNearbyMap(userLat,userLon);
      loadNearbyBooks(userLat,userLon);
    },
    ()=>{ if(status) status.textContent='❌ Could not get location.'; },
    {enableHighAccuracy:true,timeout:10000}
  );
}

function initNearbyMap(lat,lon) {
  const mapEl = document.getElementById('nearby-map');
  if(!mapEl) return;
  if(nearbyMap){nearbyMap.remove();nearbyMap=null;}
  nearbyMap=L.map('nearby-map').setView([lat,lon],13);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'© OpenStreetMap'}).addTo(nearbyMap);
  const userIcon=L.divIcon({html:'<div style="background:#2563EB;width:16px;height:16px;border-radius:50%;border:3px solid white;box-shadow:0 0 0 4px rgba(37,99,235,0.3)"></div>',className:'',iconSize:[16,16],iconAnchor:[8,8]});
  L.marker([lat,lon],{icon:userIcon}).addTo(nearbyMap).bindPopup('<b>📍 You are here</b>');
}

function loadNearbyBooks(lat,lon,q=''){
  const radius=document.getElementById('radius-select')?.value||10;
  fetch(`/books/api/nearby?lat=${lat}&lon=${lon}&radius=${radius}&q=${encodeURIComponent(q)}`)
  .then(r=>r.json()).then(books=>{
    if(!nearbyMap) return;
    nearbyMarkers.forEach(m=>nearbyMap.removeLayer(m));
    nearbyMarkers=[];
    const resultsDiv=document.getElementById('nearby-results');
    if(resultsDiv) resultsDiv.innerHTML='';
    if(!books.length){
      if(resultsDiv) resultsDiv.innerHTML='<div class="col-span-3 text-center py-8 text-gray-400"><div class="text-4xl mb-2">📚</div><p>No books found nearby. Try increasing the radius.</p></div>';
      return;
    }
    const bookIcon=L.divIcon({html:'<div style="background:#1B4332;color:white;border-radius:50%;width:36px;height:36px;display:flex;align-items:center;justify-content:center;font-size:16px;border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.3)">📚</div>',className:'',iconSize:[36,36],iconAnchor:[18,18]});
    books.forEach(b=>{
      const price = b.listing_type==='sell'?`₹${b.price}`:b.listing_type==='swap'?'Swap':'Free';
      const marker=L.marker([b.latitude,b.longitude],{icon:bookIcon}).addTo(nearbyMap)
        .bindPopup(`<div style="min-width:180px;font-family:sans-serif"><strong>${b.title}</strong><br><span style="color:#6B7280;font-size:12px">${b.distance_label}</span><br><strong style="color:#1B4332">${price}</strong><br><div style="margin-top:6px;display:flex;gap:6px"><a href="${b.wa_url}" target="_blank" style="background:#25D366;color:white;padding:4px 8px;border-radius:6px;font-size:11px;font-weight:bold;text-decoration:none">💬 WhatsApp</a><a href="${b.url}" style="background:#1B4332;color:white;padding:4px 8px;border-radius:6px;font-size:11px;font-weight:bold;text-decoration:none">View →</a></div></div>`);
      nearbyMarkers.push(marker);
      if(resultsDiv){
        const priceHtml=b.listing_type==='sell'?`<span class="text-green-700 font-bold">₹${b.price}</span>`:b.listing_type==='swap'?`<span class="text-blue-600 font-bold">Swap</span>`:`<span class="text-violet-600 font-bold">Free</span>`;
        resultsDiv.innerHTML+=`<div class="bg-white rounded-xl p-4 border border-gray-100 shadow-sm hover:shadow-md transition cursor-pointer" onclick="window.location='${b.url}'"><h4 class="font-bold text-gray-900 text-sm truncate">${b.title}</h4><p class="text-xs text-gray-500">${b.seller_name} · ${b.distance_label}</p><div class="mt-1">${priceHtml}</div><div class="flex gap-2 mt-3"><a href="${b.wa_url}" target="_blank" onclick="event.stopPropagation()" class="flex-1 bg-green-500 text-white text-xs font-bold py-2 rounded-lg text-center">💬 WhatsApp</a><a href="tel:+91${b.seller_phone.replace(/\D/g,'')}" onclick="event.stopPropagation()" class="flex-1 bg-gray-100 text-gray-700 text-xs font-bold py-2 rounded-lg text-center">📞 Call</a></div></div>`;
      }
    });
    if(nearbyMarkers.length) nearbyMap.fitBounds(L.featureGroup(nearbyMarkers).getBounds().pad(0.2));
  });
}

function updateNearbyRadius(){ if(userLat&&userLon) loadNearbyBooks(userLat,userLon); }

// ── FORM HELPERS ────────────────────────────────────────────────
function selectListingType(type,el){
  document.querySelectorAll('.listing-type-btn').forEach(b=>{b.style.borderColor='#E5E7EB';b.style.background='white';});
  el.style.borderColor=type==='sell'?'#16A34A':type==='swap'?'#2563EB':'#7C3AED';
  el.style.background=type==='sell'?'#F0FDF4':type==='swap'?'#EFF6FF':'#F5F3FF';
  const priceField = document.getElementById('price-field');
  const typeInput = document.getElementById('listing-type-input');
  if(priceField) priceField.classList.toggle('hidden', type!=='sell');
  if(typeInput) typeInput.value = type;
}

function previewCoverImage(input){
  if(input.files&&input.files[0]){
    const r=new FileReader();
    r.onload=e=>{
      document.getElementById('cover-preview').src=e.target.result;
      document.getElementById('cover-preview').classList.remove('hidden');
      document.getElementById('upload-placeholder').classList.add('hidden');
    };
    r.readAsDataURL(input.files[0]);
  }
}

function validateListForm(){
  const lat=parseFloat(document.getElementById('lat-input')?.value||0);
  const lon=parseFloat(document.getElementById('lon-input')?.value||0);
  if(!lat||!lon||(lat===0&&lon===0)){
    alert('⚠️ Please click "Use My Current Location" to set your location before listing.');
    document.getElementById('location-btn')?.scrollIntoView({behavior:'smooth'});
    return false;
  }
  return true;
}
