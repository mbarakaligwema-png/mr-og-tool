package com.mrog.admin;

import android.accessibilityservice.AccessibilityService;
import android.view.accessibility.AccessibilityEvent;
import android.widget.Toast;
import android.util.Log;

public class MyAccessibilityService extends AccessibilityService {

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        if (event.getEventType() == AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED) {
            String className = event.getClassName() != null ? event.getClassName().toString().toLowerCase() : "";

            // Detect Factory Reset screens keywords
            if (className.contains("factoryreset") || className.contains("resetsettings")
                    || className.contains("masterclear")) {
                Log.d("MROG_ACC", "Blocked Restricted Screen: " + className);
                performGlobalAction(GLOBAL_ACTION_BACK);
                performGlobalAction(GLOBAL_ACTION_HOME);
                Toast.makeText(this, "Action Blocked by Administrator", Toast.LENGTH_SHORT).show();
            }
        }
    }

    @Override
    public void onInterrupt() {
    }
}
