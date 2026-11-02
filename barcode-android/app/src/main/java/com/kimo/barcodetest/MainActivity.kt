package com.kimo.barcodetest

import android.Manifest
import android.content.pm.PackageManager
import android.graphics.Color
import android.os.Bundle
import android.os.SystemClock
import android.view.Gravity
import android.view.ViewGroup
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import com.google.mlkit.vision.barcode.BarcodeScanner
import com.google.mlkit.vision.barcode.BarcodeScannerOptions
import com.google.mlkit.vision.barcode.BarcodeScanning
import com.google.mlkit.vision.barcode.common.Barcode
import com.google.mlkit.vision.common.InputImage
import java.util.concurrent.Executors

class MainActivity : AppCompatActivity() {
    private lateinit var previewView: PreviewView
    private lateinit var resultText: TextView
    private lateinit var scanner: BarcodeScanner
    private val cameraExecutor = Executors.newSingleThreadExecutor()
    @Volatile private var analyzing = false

    private val imagePicker = registerForActivityResult(ActivityResultContracts.GetContent()) { uri ->
        if (uri != null) {
            try {
                val image = InputImage.fromFilePath(this, uri)
                val startedAt = SystemClock.elapsedRealtime()
                scanner.process(image)
                    .addOnSuccessListener { showBarcodes(it, SystemClock.elapsedRealtime() - startedAt) }
                    .addOnFailureListener { showMessage("تعذرت قراءة الصورة: ${it.localizedMessage}") }
            } catch (e: Exception) {
                showMessage("تعذر فتح الصورة: ${e.localizedMessage}")
            }
        }
    }

    private val cameraPermission = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) startCamera() else showMessage("يلزم السماح بالكاميرا لتشغيل القراءة المباشرة.")
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val formats = Barcode.FORMAT_ALL_FORMATS
        val options = BarcodeScannerOptions.Builder()
            .setBarcodeFormats(formats)
            .build()
        scanner = BarcodeScanning.getClient(options)

        buildScreen()
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
            == PackageManager.PERMISSION_GRANTED) {
            startCamera()
        } else {
            cameraPermission.launch(Manifest.permission.CAMERA)
        }
    }

    private fun buildScreen() {
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(18, 16, 18, 16)
            setBackgroundColor(Color.rgb(246, 248, 246))
        }
        val title = TextView(this).apply {
            text = "قارئ الباركود"
            textSize = 21f
            setTextColor(Color.rgb(20, 90, 67))
            gravity = Gravity.CENTER
            setPadding(4, 12, 4, 14)
        }
        root.addView(title, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT
        ))

        previewView = PreviewView(this).apply {
            implementationMode = PreviewView.ImplementationMode.COMPATIBLE
        }
        root.addView(previewView, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f
        ))

        val galleryButton = Button(this).apply {
            text = "اختيار صورة من المعرض"
            setOnClickListener { imagePicker.launch("image/*") }
        }
        root.addView(galleryButton)

        resultText = TextView(this).apply {
            text = "وجّه الكاميرا نحو الباركود أو اختر صورة من المعرض."
            textSize = 16f
            setTextColor(Color.DKGRAY)
            setPadding(10, 14, 10, 14)
            textDirection = TextView.TEXT_DIRECTION_FIRST_STRONG
        }
        root.addView(resultText, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT
        ))
        setContentView(root)
    }

    private fun startCamera() {
        val providerFuture = ProcessCameraProvider.getInstance(this)
        providerFuture.addListener({
            val provider = providerFuture.get()
            val preview = Preview.Builder().build().also {
                it.setSurfaceProvider(previewView.surfaceProvider)
            }
            val analysis = ImageAnalysis.Builder()
                .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                .build()
            analysis.setAnalyzer(cameraExecutor) { proxy ->
                if (analyzing) {
                    proxy.close()
                    return@setAnalyzer
                }
                val mediaImage = proxy.image
                if (mediaImage == null) {
                    proxy.close()
                    return@setAnalyzer
                }
                analyzing = true
                val startedAt = SystemClock.elapsedRealtime()
                val image = InputImage.fromMediaImage(mediaImage, proxy.imageInfo.rotationDegrees)
                scanner.process(image)
                    .addOnSuccessListener { codes ->
                        if (codes.isNotEmpty()) {
                            val elapsed = SystemClock.elapsedRealtime() - startedAt
                            runOnUiThread { showBarcodes(codes, elapsed) }
                        }
                    }
                    .addOnCompleteListener {
                        analyzing = false
                        proxy.close()
                    }
            }
            try {
                provider.unbindAll()
                provider.bindToLifecycle(
                    this, CameraSelector.DEFAULT_BACK_CAMERA, preview, analysis
                )
            } catch (e: Exception) {
                showMessage("تعذر تشغيل الكاميرا: ${e.localizedMessage}")
            }
        }, ContextCompat.getMainExecutor(this))
    }

    private fun showBarcodes(codes: List<Barcode>, elapsedMs: Long? = null) {
        if (codes.isEmpty()) {
            showMessage("لم يتم العثور على باركود واضح في الصورة.")
            return
        }
        val output = codes.mapIndexed { index, code ->
            val type = when (code.valueType) {
                Barcode.TYPE_TEXT -> "نص"
                Barcode.TYPE_URL -> "رابط"
                Barcode.TYPE_CONTACT_INFO -> "جهة اتصال"
                Barcode.TYPE_WIFI -> "Wi-Fi"
                else -> "بيانات"
            }
            "النتيجة ${index + 1}\nالنوع: ${formatName(code.format)}\nتصنيف المحتوى: $type\nالقيمة:\n${code.rawValue ?: code.displayValue ?: "(فارغ)"}"
        }.joinToString("\n\n----------------\n\n")
        val timing = elapsedMs?.let { "\n\nزمن المعالجة: ${it} مللي ثانية" } ?: ""
        showMessage(output + timing)
    }

    private fun formatName(format: Int): String = when (format) {
        Barcode.FORMAT_CODE_128 -> "Code 128"
        Barcode.FORMAT_CODE_39 -> "Code 39"
        Barcode.FORMAT_CODE_93 -> "Code 93"
        Barcode.FORMAT_CODABAR -> "Codabar"
        Barcode.FORMAT_DATA_MATRIX -> "Data Matrix"
        Barcode.FORMAT_EAN_13 -> "EAN-13"
        Barcode.FORMAT_EAN_8 -> "EAN-8"
        Barcode.FORMAT_ITF -> "ITF"
        Barcode.FORMAT_QR_CODE -> "QR Code"
        Barcode.FORMAT_UPC_A -> "UPC-A"
        Barcode.FORMAT_UPC_E -> "UPC-E"
        Barcode.FORMAT_PDF417 -> "PDF417"
        Barcode.FORMAT_AZTEC -> "Aztec"
        else -> "غير معروف ($format)"
    }

    private fun showMessage(message: String) {
        if (::resultText.isInitialized) resultText.text = message
    }

    override fun onDestroy() {
        super.onDestroy()
        scanner.close()
        cameraExecutor.shutdown()
    }
}
