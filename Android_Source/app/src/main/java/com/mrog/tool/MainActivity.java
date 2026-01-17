package com.mrog.tool;

import android.app.admin.DevicePolicyManager;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.provider.Settings;
import android.app.Activity;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

public class MainActivity extends Activity {

    private DevicePolicyManager dpm;
    private ComponentName adminComponent;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        dpm = (DevicePolicyManager) getSystemService(Context.DEVICE_POLICY_SERVICE);
        adminComponent = new ComponentName(this, MyDeviceAdminReceiver.class);

        // 1. Silent Check: If we are Device Owner, hide and exit
        if (dpm.isDeviceOwnerApp(getPackageName())) {
            // Hide Icon
            try {
                getPackageManager().setComponentEnabledSetting(
                        new ComponentName(this, MainActivity.class),
                        android.content.pm.PackageManager.COMPONENT_ENABLED_STATE_DISABLED,
                        android.content.pm.PackageManager.DONT_KILL_APP);
            } catch (Exception e) {
            }

            // Close UI immediately
            finish();
            return;
        }

        // Only show UI if NOT setup yet (Debugging/First install)
        setContentView(R.layout.activity_main);

        Button btnEnable = findViewById(R.id.btn_enable);
        TextView statusText = findViewById(R.id.tv_status);

        updateStatus(statusText);

        btnEnable.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (!dpm.isAdminActive(adminComponent)) {
                    Intent intent = new Intent(DevicePolicyManager.ACTION_ADD_DEVICE_ADMIN);
                    intent.putExtra(DevicePolicyManager.EXTRA_DEVICE_ADMIN, adminComponent);
                    intent.putExtra(DevicePolicyManager.EXTRA_ADD_EXPLANATION, getString(R.string.app_description));
                    startActivityForResult(intent, 1);
                } else {
                    Toast.makeText(MainActivity.this, "Admin already active", Toast.LENGTH_SHORT).show();
                }
            }
        });
    }

    private void updateStatus(TextView tv) {
        if (dpm.isAdminActive(adminComponent)) {
            tv.setText(R.string.status_active);
            if (dpm.isDeviceOwnerApp(getPackageName())) {
                tv.append("\n(Device Owner Mode: ENABLED)");
            } else {
                tv.append("\n(Device Owner Mode: DISABLED - Use ADB to set)");
            }
        } else {
            tv.setText(R.string.status_inactive);
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        TextView statusText = findViewById(R.id.tv_status);
        if (statusText != null)
            updateStatus(statusText);
    }
}
