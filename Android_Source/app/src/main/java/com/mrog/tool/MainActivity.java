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
        
        // Simple UI Layout Programmatically (avoiding complex XML for simplicity if user just builds)
        // But better to use the one we can imagine or just set content view to a simple layout if we had one.
        // For robustness, I'll create a layout file or just use simple logic here.
        // Let's stick to the standard R.layout if we generated it, or keep it simple.
        // I didn't generate layout XMLs yet other than device_admin. Let's make a simple one here.
        
        setContentView(R.layout.activity_main);

        dpm = (DevicePolicyManager) getSystemService(Context.DEVICE_POLICY_SERVICE);
        adminComponent = new ComponentName(this, MyDeviceAdminReceiver.class);
        
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
                    // If active, try to re-apply poliices just in case
                    // This requires us to be Device Owner to really do much
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
        if(statusText != null) updateStatus(statusText);
    }
}
