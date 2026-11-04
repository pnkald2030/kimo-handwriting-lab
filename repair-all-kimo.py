from pathlib import Path
import re,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "Kimo_Repair_Package")
h=root/"www/index.html";s=h.read_text(encoding="utf-8")
def rep(a,b,n):
 global s
 if b in s:return
 if a not in s:raise SystemExit("Missing patch anchor: "+n)
 s=s.replace(a,b,1)

rep("slot.addEventListener('click',()=>{if(src){openImageLightbox(src);}else{$('docImage').value='';$('docImage').click();}});","slot.addEventListener('click',()=>{if(src){openImageLightbox(src);}else{openKimoImageSourceChooser(i);}});","image slot")
chooser=r'''let kimoImagePickTargetIndex=-1,kimoImagePickReplace=false;
function openKimoImageSourceChooser(index,replace=false){
 kimoImagePickTargetIndex=Number.isInteger(index)?index:-1;kimoImagePickReplace=!!replace;
 let modal=document.getElementById('kimoImageSourceChooser');
 if(!modal){modal=document.createElement('div');modal.id='kimoImageSourceChooser';modal.className='modal kimo-image-source-chooser';
 modal.innerHTML='<div class="sheet"><div class="sheet-head"><h3>إضافة صورة الوثيقة</h3><button type="button" class="close" data-kimo-image-close>×</button></div><p>اختر مصدر الصورة</p><div class="kimo-image-source-actions"><button type="button" data-kimo-image-source="camera">📷 التصوير بالكاميرا</button><button type="button" data-kimo-image-source="gallery">▧ اختيار من المعرض</button></div></div>';
 document.body.appendChild(modal);modal.addEventListener('click',e=>{if(e.target===modal||e.target.closest('[data-kimo-image-close]')){modal.classList.add('hidden');kimoImagePickTargetIndex=-1;kimoImagePickReplace=false;return;}const a=e.target.closest('[data-kimo-image-source]');if(!a)return;modal.classList.add('hidden');const input=document.getElementById(a.dataset.kimoImageSource==='camera'?'cameraImage':'docImage');if(input){input.value='';input.click();}});}
 modal.classList.remove('hidden');
}
'''
rep("function renderImagePreviews(){",chooser+"function renderImagePreviews(){","chooser function")
rep("replace.addEventListener('click',()=>replaceInput.click());","replace.addEventListener('click',()=>openKimoImageSourceChooser(i,true));","replace chooser")
old=""" try{for(const file of incoming){const empty=pendingImages.findIndex(x=>!x);const index=empty>=0?empty:pendingImages.length<3?pendingImages.length:-1;if(index<0)throw new Error('الحد الاقصى 3 صور');pendingImages[index]=await readImage(file);}}
 catch(err){toast(err.message||'تعذر تحميل الصورة');}
 pendingImage=pendingImages.find(Boolean)||null;removeExistingImage=false;renderImagePreviews();if(input)input.value='';
}"""
new=""" try{for(const file of incoming){let index=-1;if(kimoImagePickTargetIndex>=0&&kimoImagePickTargetIndex<3&&(kimoImagePickReplace||!pendingImages[kimoImagePickTargetIndex])){index=kimoImagePickTargetIndex;kimoImagePickTargetIndex=-1;kimoImagePickReplace=false;}else{index=pendingImages.findIndex(x=>!x);if(index<0)index=pendingImages.length<3?pendingImages.length:-1;}if(index<0)throw new Error('الحد الأقصى 3 صور');pendingImages[index]=await readImage(file);}}
 catch(err){toast(err.message||'تعذر تحميل الصورة');}
 kimoImagePickTargetIndex=-1;kimoImagePickReplace=false;pendingImage=pendingImages.find(Boolean)||null;removeExistingImage=false;renderImagePreviews();if(input)input.value='';
}"""
rep(old,new,"image handler")
css='''<style id="kimo-image-source-chooser-style">#kimoImageSourceChooser{z-index:100500;display:flex;align-items:flex-end;justify-content:center;background:#0008;padding:12px}#kimoImageSourceChooser.hidden{display:none!important}#kimoImageSourceChooser .sheet{width:min(100%,440px);border-radius:20px;padding:16px;background:var(--card,#fff);color:var(--text,#222);box-shadow:0 15px 45px #0004}#kimoImageSourceChooser .sheet-head{display:flex;align-items:center;justify-content:space-between;gap:10px}#kimoImageSourceChooser .sheet-head h3{margin:0;font-size:16px}#kimoImageSourceChooser .close{border:0;border-radius:50%;width:34px;height:34px;font-size:24px;background:#f2e8e7;color:#704244}#kimoImageSourceChooser p{margin:8px 0 12px;color:var(--muted,#777);font-size:12px}#kimoImageSourceChooser .kimo-image-source-actions{display:grid;grid-template-columns:1fr 1fr;gap:9px}#kimoImageSourceChooser .kimo-image-source-actions button{border:1px solid var(--border,#ddd);border-radius:12px;background:var(--surface-secondary,#f7f5f4);color:var(--text,#222);padding:14px 8px;font-weight:800;font-size:13px}</style>'''
if "kimo-image-source-chooser-style" not in s:s=s.replace("</body></html>",css+"\n</body></html>",1)

# Patch both share actions to prefer the native Android share sheet.
s=re.sub(r"(?s)  const files=\[\];for\(let i=0;i<sources\.length;i\+\+\)\{.*?\n  else\{toast\('مشاركة الصور غير مدعومة في هذا المتصفح'\);\}",
"""  if(window.KimoBarcodeNative?.shareImages){await window.KimoBarcodeNative.shareImages({dataUrls:sources,title:'مشاركة صور وثيقة من كيمو'});return;}
  const files=[];for(let i=0;i<sources.length;i++){const response=await fetch(sources[i]);const blob=await response.blob();const mime=blob.type||'image/jpeg';const ext=mime.includes('png')?'png':mime.includes('webp')?'webp':'jpg';files.push(new File([blob],'kimo-document-'+(i+1)+'.'+ext,{type:mime}));}
  if(navigator.share&&navigator.canShare&&navigator.canShare({files})){await navigator.share({files});}
  else{toast('المشاركة غير مدعومة في هذه النسخة.');}""",s,count=1)
old="async function shareLightboxImage(){if(!activeLightboxImage)return;try{const res=await fetch(activeLightboxImage);const blob=await res.blob();const file=new File([blob],'kimo-document.jpg',{type:blob.type||'image/jpeg'});if(navigator.canShare&&navigator.canShare({files:[file]})){await navigator.share({files:[file],title:'صورة الوثيقة'});}else if(navigator.share){await navigator.share({title:'صورة الوثيقة',text:'صورة وثيقة من أرشيف كيمو'});}else{await navigator.clipboard.writeText(activeLightboxImage);toast('المشاركة غير مدعومة هنا؛ تم نسخ رابط الصورة إن أمكن.');}}catch(e){if(e.name!=='AbortError')toast('تعذرت مشاركة الصورة على هذا المتصفح.')}}"
new="async function shareLightboxImage(){if(!activeLightboxImage)return;try{if(window.KimoBarcodeNative?.shareImages){await window.KimoBarcodeNative.shareImages({dataUrls:[activeLightboxImage],title:'مشاركة صورة وثيقة من كيمو'});return;}const res=await fetch(activeLightboxImage);const blob=await res.blob();const file=new File([blob],'kimo-document.jpg',{type:blob.type||'image/jpeg'});if(navigator.canShare&&navigator.canShare({files:[file]})){await navigator.share({files:[file],title:'صورة الوثيقة'});}else{toast('المشاركة غير مدعومة في هذه النسخة.');}}catch(e){if(e.name!=='AbortError')toast('تعذرت مشاركة الصورة على هذا المتصفح.')}}"
rep(old,new,"share lightbox")
rep("$('docType').addEventListener('change',()=>{updateLabels();updateShortAreaLabels()});","$('docType').addEventListener('change',()=>{updateLabels();updateShortAreaLabels();configureInheritanceFields({})});","inheritance section")
rep("if(addButton)addButton.onclick=()=>{","if(addButton)addButton.onclick=(event)=>{event.preventDefault();event.stopPropagation();","heirs button")
old="function readImage(file){return new Promise((resolve,reject)=>{if(file.size>12*1024*1024){reject(new Error('حجم الصورة أكبر من 12 ميغابايت. اختر صورة أصغر.'));return}let r=new FileReader();r.onload=()=>{let img=new Image();img.onload=()=>{try{let max=2600,scale=Math.min(1.5,max/Math.max(img.width,img.height)),w=Math.max(1,Math.round(img.width*scale)),h=Math.max(1,Math.round(img.height*scale));let c=document.createElement('canvas');c.width=w;c.height=h;c.getContext('2d').drawImage(img,0,0,w,h);resolve(c.toDataURL('image/jpeg',.84))}catch(e){resolve(r.result)}};img.onerror=()=>resolve(r.result);img.src=r.result};r.onerror=()=>reject(new Error('تعذرت قراءة الصورة'));r.readAsDataURL(file)})}"
new="function readImage(file){return new Promise((resolve,reject)=>{if(file.size>12*1024*1024){reject(new Error('حجم الصورة أكبر من 12 ميغابايت. اختر صورة أصغر.'));return}let r=new FileReader();r.onload=()=>{let img=new Image();img.onload=()=>{try{let max=2200,scale=Math.min(1,max/Math.max(img.width,img.height)),w=Math.max(1,Math.round(img.width*scale)),h=Math.max(1,Math.round(img.height*scale));let c=document.createElement('canvas');c.width=w;c.height=h;let ctx=c.getContext('2d',{alpha:false});ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';ctx.drawImage(img,0,0,w,h);resolve(c.toDataURL('image/jpeg',.82));c.width=1;c.height=1;img.src='';}catch(e){resolve(r.result)}};img.onerror=()=>resolve(r.result);img.src=r.result};r.onerror=()=>reject(new Error('تعذرت قراءة الصورة'));r.readAsDataURL(file)})}"
rep(old,new,"image optimization")
rep("async function render(){let docs=await dbAll();","let kimoRenderGeneration=0;\nasync function render(){const renderId=++kimoRenderGeneration;let docs=await dbAll();if(renderId!==kimoRenderGeneration)return;","render generation")
rep("if(app?.exitApp){app.exitApp();return}toastMessage('للخروج أغلق التطبيق من قائمة التطبيقات المفتوحة');return","if(app?.exitApp){app.exitApp();return}if(window.KimoBarcodeNative?.exitApp){window.KimoBarcodeNative.exitApp();return}toastMessage('للخروج أغلق التطبيق من قائمة التطبيقات المفتوحة');return","back exit")
rep("setZoomRatio: opts => nativePlugin.setZoomRatio(typeof opts==='number'?{ratio:opts}:opts||{})","setZoomRatio: opts => nativePlugin.setZoomRatio(typeof opts==='number'?{ratio:opts}:opts||{}),\n    shareImages: opts => nativePlugin.shareImages(opts||{}),\n    exitApp: () => nativePlugin.exitApp()","native bridge")
h.write_text(s,encoding="utf-8")

# Add native sharing and exit.
plug=root/"android-native/src/main/java/com/kimo/archive/KimoBarcodeNativePlugin.kt";k=plug.read_text()
if "fun shareImages(call: PluginCall)" not in k:
 k=k.replace("import android.content.Intent\n","import android.content.Intent\nimport android.content.ClipData\nimport android.net.Uri\nimport androidx.core.content.FileProvider\nimport java.io.File\n",1)
 marker="    @PluginMethod fun stopCamera(call: PluginCall) { call.resolve() }"
 methods=r'''    @PluginMethod
    fun shareImages(call: PluginCall) {
        try {
            val dataUrls = call.getArray("dataUrls") ?: JSArray()
            if (dataUrls.length() == 0) { call.reject("لا توجد صور للمشاركة"); return }
            val folder = File(context.cacheDir, "kimo-share")
            if (!folder.exists()) folder.mkdirs()
            val uris = ArrayList<Uri>()
            for (i in 0 until dataUrls.length()) {
                val dataUrl = dataUrls.getString(i) ?: continue
                val header = dataUrl.substringBefore(',')
                val mime = Regex("data:([^;]+)").find(header)?.groupValues?.getOrNull(1) ?: "image/jpeg"
                val ext = when (mime.lowercase()) { "image/png" -> "png"; "image/webp" -> "webp"; else -> "jpg" }
                val bytes = Base64.decode(dataUrl.substringAfter(',', dataUrl), Base64.DEFAULT)
                val file = File(folder, "kimo-" + System.currentTimeMillis().toString() + "-$i.$ext")
                file.writeBytes(bytes)
                uris.add(FileProvider.getUriForFile(context, context.packageName + ".kimo.fileprovider", file))
            }
            if (uris.isEmpty()) { call.reject("تعذرت قراءة الصور المحددة"); return }
            val send = Intent(Intent.ACTION_SEND_MULTIPLE).apply {
                type = "image/*"
                putParcelableArrayListExtra(Intent.EXTRA_STREAM, uris)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                val clip = ClipData.newUri(context.contentResolver, "صور وثيقة كيمو", uris[0])
                for (uri in uris.drop(1)) clip.addItem(ClipData.Item(uri))
                clipData = clip
                putExtra(Intent.EXTRA_TITLE, call.getString("title") ?: "مشاركة صور من كيمو")
            }
            activity.startActivity(Intent.createChooser(send, call.getString("title") ?: "مشاركة صور من كيمو"))
            call.resolve(JSObject().put("shared", true))
        } catch (e: Exception) { call.reject(e.message ?: "تعذرت مشاركة الصور") }
    }
    @PluginMethod
    fun exitApp(call: PluginCall) {
        activity.runOnUiThread { activity.finish() }
        call.resolve()
    }
'''
 if marker not in k:raise SystemExit("Native plugin anchor missing")
 plug.write_text(k.replace(marker,methods+marker,1))

# Full-screen native scanner with pinch and automatic zoom.
cam=root/"android-native/src/main/java/com/kimo/archive/KimoBarcodeScannerActivity.kt";k=cam.read_text()
if "ScaleGestureDetector" not in k:
 k=k.replace("import android.view.Gravity\n","import android.view.Gravity\nimport android.view.ScaleGestureDetector\n",1)
 k=k.replace("    private var scanner: com.google.mlkit.vision.barcode.BarcodeScanner? = null\n","    private var scanner: com.google.mlkit.vision.barcode.BarcodeScanner? = null\n    private var camera: androidx.camera.core.Camera? = null\n    private var currentZoom = 1f\n    private var scanStartedAt = 0L\n    private var lastAutoZoomStep = 0\n    private lateinit var scaleDetector: ScaleGestureDetector\n",1)
 old='''        val hint = TextView(this).apply {
            text = "وجّه الكاميرا نحو الرمز\\nسيتم التقاطه تلقائياً عند وضوحه\\n\\nاضغط هنا للإلغاء"
            setTextColor(-1); textSize = 16f; gravity = Gravity.CENTER
            setPadding(24, 18, 24, 18); setBackgroundColor(0x99000000.toInt())
            setOnClickListener { finishCancelled() }
        }
        val lp = FrameLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT, Gravity.CENTER)
        root.addView(hint, lp)
        setContentView(root)
'''
 new='''        val hint = TextView(this).apply {
            text = "وجّه الكاميرا نحو الرمز\\nسيتم التقاطه تلقائياً عند وضوحه\\nقرّب أو أبعد إصبعين للتقريب"
            setTextColor(-1); textSize = 14f; gravity = Gravity.CENTER
            setPadding(20, 14, 20, 14); setBackgroundColor(0x77000000.toInt())
            isClickable = false; isFocusable = false
        }
        val lp = FrameLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT, Gravity.CENTER)
        root.addView(hint, lp)
        val close = TextView(this).apply {
            text = "×"; textSize = 32f; gravity = Gravity.CENTER; setTextColor(-1)
            setBackgroundColor(0x99000000.toInt()); setPadding(10, 0, 10, 4)
            setOnClickListener { finishCancelled() }
        }
        val closeLp = FrameLayout.LayoutParams(56, 56, Gravity.TOP or Gravity.END).apply { topMargin = 24; marginEnd = 16 }
        root.addView(close, closeLp)
        scaleDetector = ScaleGestureDetector(this, object : ScaleGestureDetector.SimpleOnScaleGestureListener() {
            override fun onScale(detector: ScaleGestureDetector): Boolean {
                val state = camera?.cameraInfo?.zoomState?.value ?: return false
                currentZoom = (currentZoom * detector.scaleFactor).coerceIn(state.minZoomRatio, state.maxZoomRatio)
                camera?.cameraControl?.setZoomRatio(currentZoom)
                return true
            }
        })
        previewView.setOnTouchListener { _, event -> scaleDetector.onTouchEvent(event); true }
        setContentView(root)
'''
 if old not in k:raise SystemExit("Scanner UI anchor missing")
 k=k.replace(old,new,1)
 k=k.replace("                analysis.setAnalyzer(executor) { proxy ->","                scanStartedAt = System.currentTimeMillis()\n                lastAutoZoomStep = 0\n                analysis.setAnalyzer(executor) { proxy ->",1)
 k=k.replace("                            ?.addOnCompleteListener { proxy.close() }",'''                            ?.addOnCompleteListener {
                                proxy.close()
                                if (!delivered.get()) {
                                    val elapsed = System.currentTimeMillis() - scanStartedAt
                                    val step = when { elapsed >= 10000 -> 3; elapsed >= 6500 -> 2; elapsed >= 3500 -> 1; else -> 0 }
                                    if (step > lastAutoZoomStep) {
                                        lastAutoZoomStep = step
                                        val target = when (step) { 1 -> 1.35f; 2 -> 1.75f; else -> 2.2f }
                                        runOnUiThread {
                                            val state = camera?.cameraInfo?.zoomState?.value
                                            if (state != null) {
                                                currentZoom = target.coerceIn(state.minZoomRatio, state.maxZoomRatio)
                                                camera?.cameraControl?.setZoomRatio(currentZoom)
                                            }
                                        }
                                    }
                                }
                            }''',1)
 k=k.replace("                cameraProvider?.bindToLifecycle(this, CameraSelector.DEFAULT_BACK_CAMERA, preview, analysis)","                camera = cameraProvider?.bindToLifecycle(this, CameraSelector.DEFAULT_BACK_CAMERA, preview, analysis)\n                currentZoom = 1f",1)
 k=k.replace("        cameraProvider?.unbindAll()\n        scanner?.close()","        cameraProvider?.unbindAll()\n        camera = null\n        scanner?.close()",1)
 cam.write_text(k)

# Build patcher: share provider and dispatch Android back to the HTML state machine.
patcher=root/"patch-android.py";p=patcher.read_text()
p=re.sub(r"(?m)^if 'kotlinOptions' not in s and 'android \{' in s:\n    s=s.replace\('android \{', .*?\n","",p)
if "kimo.fileprovider" not in p:
 marker="# Register native Capacitor plugin and fit content within system bars.\n"
 add='''# Share local document images safely through Android's chooser.
res_xml=app/'src/main/res/xml'
res_xml.mkdir(parents=True,exist_ok=True)
(res_xml/'kimo_file_paths.xml').write_text('<paths xmlns:android="http://schemas.android.com/apk/res/android"><cache-path name="kimo_share" path="kimo-share/" /></paths>')
manifest=app/'src/main/AndroidManifest.xml'
m=manifest.read_text()
if 'kimo.fileprovider' not in m:
    provider='        <provider android:name="androidx.core.content.FileProvider" android:authorities="' + chr(36) + '{applicationId}.kimo.fileprovider" android:exported="false" android:grantUriPermissions="true"><meta-data android:name="android.support.FILE_PROVIDER_PATHS" android:resource="@xml/kimo_file_paths" /></provider>\\n'
    m=m.replace('</application>',provider+'    </application>')
manifest.write_text(m)

'''
 if marker not in p:raise SystemExit("Patcher anchor missing")
 p=p.replace(marker,add+marker,1)
if "onBackPressed()" not in p:
 p=p.replace("        main.write_text(code)\n","""        if 'onBackPressed()' not in code:
            code=code.replace('    }\n}', '    }\n    @Override\n    public void onBackPressed() {\n        if (getBridge() != null && getBridge().getWebView() != null) {\n            getBridge().getWebView().evaluateJavascript("window.__kimoHandleAndroidBack && window.__kimoHandleAndroidBack()", null);\n        } else { super.onBackPressed(); }\n    }\n}')
        main.write_text(code)
""",1)
patcher.write_text(p)
print("Kimo repair patch applied")
