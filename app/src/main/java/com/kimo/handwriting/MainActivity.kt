
package com.kimo.handwriting

import android.app.Activity
import android.os.Bundle
import android.content.Intent
import android.graphics.BitmapFactory
import android.graphics.Color
import android.view.Gravity
import android.widget.*
import java.io.File

class MainActivity : Activity() {

    private lateinit var preview: ImageView
    private lateinit var status: TextView
    private lateinit var folder: File

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        folder = File(filesDir, "documents")
        folder.mkdirs()

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER_HORIZONTAL
            setPadding(24, 30, 24, 30)
            setBackgroundColor(Color.rgb(245, 248, 245))
        }

        val title = TextView(this).apply {
            text = "كيمو"
            textSize = 32f
            setTextColor(Color.rgb(20, 105, 70))
            gravity = Gravity.CENTER
        }

        val subtitle = TextView(this).apply {
            text = "إرشيف الوثائق الذكي"
            textSize = 20f
            setTextColor(Color.DKGRAY)
            gravity = Gravity.CENTER
        }

        val choose = Button(this).apply {
            text = "اختيار صورة وثيقة"
            setOnClickListener {
                val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
                    type = "image/*"
                    addCategory(Intent.CATEGORY_OPENABLE)
                }
                startActivityForResult(intent, 100)
            }
        }

        preview = ImageView(this).apply {
            adjustViewBounds = true
            scaleType = ImageView.ScaleType.FIT_CENTER
        }

        status = TextView(this).apply {
            text = "اختر صورة للبدء"
            textSize = 16f
            setTextColor(Color.DKGRAY)
            gravity = Gravity.CENTER
        }

        layout.addView(title)
        layout.addView(subtitle)
        layout.addView(choose)
        layout.addView(status)

        layout.addView(
            preview,
            LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                0,
                1f
            )
        )

        setContentView(layout)
    }

    override fun onActivityResult(
        requestCode: Int,
        resultCode: Int,
        data: Intent?
    ) {
        super.onActivityResult(requestCode, resultCode, data)

        if (requestCode == 100 && resultCode == RESULT_OK) {
            val uri = data?.data ?: return

            try {
                val name = "document_${System.currentTimeMillis()}.jpg"
                val destination = File(folder, name)

                contentResolver.openInputStream(uri).use { input ->
                    requireNotNull(input) { "تعذر قراءة الصورة" }
                    destination.outputStream().use { output ->
                        input.copyTo(output)
                    }
                }

                val bitmap = BitmapFactory.decodeFile(destination.absolutePath)
                    ?: throw Exception("تعذر فتح الصورة")

                preview.setImageBitmap(bitmap)
                status.text = "تم حفظ الوثيقة داخل الهاتف بنجاح"

            } catch (e: Exception) {
                status.text = "تعذر حفظ الصورة: ${e.message}"
            }
        }
    }
}
