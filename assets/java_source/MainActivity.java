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

        // Hide from launcher? (Optional)
        // getPackageManager().setComponentEnabledSetting(getComponentName(),
        // PackageManager.COMPONENT_ENABLED_STATE_DISABLED,
        // PackageManager.DONT_KILL_APP);

        finish(); // Close immediately to be stealthy
    }
}
