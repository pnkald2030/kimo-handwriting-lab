package com.kimo.handwriting

import android.app.Activity
import android.os.Bundle
import android.graphics.Color
import android.view.Gravity
import android.widget.LinearLayout
import android.widget.TextView

class MainActivity : Activity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(28, 40, 28, 40)
            setBackgroundColor(Color.rgb(245, 248, 245))
        }

        val title = TextView(this).apply {
            text = "كيمو"
            textSize = 34f
            setTextColor(Color.rgb(20, 105, 70))
            gravity = Gravity.CENTER
        }

        val subtitle = TextView(this).apply {
            text = "إرشيف الوثائق الذكي"
            textSize = 21f
            setTextColor(Color.DKGRAY)
            gravity = Gravity.CENTER
        }

        val message = TextView(this).apply {
            text = "\nمرحباً بك في مختبر كيمو\n\nهنا سنختبر استخراج النصوص العربية\nالمطبوعة والمكتوبة بخط اليد."
            textSize = 17f
            setTextColor(Color.DKGRAY)
            gravity = Gravity.CENTER
        }

        layout.addView(title)
        layout.addView(subtitle)
        layout.addView(message)

        setContentView(layout)
    }
}
