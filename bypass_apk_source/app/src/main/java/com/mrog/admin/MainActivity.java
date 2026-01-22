package com.mrog.admin;

import android.app.admin.DevicePolicyManager;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.os.UserManager;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // Hakuna layout tunayohitaji sana, lakini tunaweza kuweka simple view au kuacha
        // default
        // Kama huna R.layout.activity_main, unaweza kuondoa mstari huu au kutengeneza
        // layout simple.
        // Kwa sasa nita-comment ili isilete error kama layout haipo,
        // ila kama unayo layout, ondoa comment.
        // setContentView(R.layout.activity_main);

        applyRestrictions();
    }

    private void applyRestrictions() {
        DevicePolicyManager dpm = (DevicePolicyManager) getSystemService(Context.DEVICE_POLICY_SERVICE);
        ComponentName adminComponent = new ComponentName(this, MyDeviceAdminReceiver.class);

        // Angalia kama sisi ni Device Owner
        if (dpm.isDeviceOwnerApp(getPackageName())) {

            try {
                // Tuma Broadcast kwa Receiver ili afanye kazi nzito (Kuepuka duplicate code)
                // Hii inahakikisha logic yote iko sehemu moja (MyDeviceAdminReceiver)
                Intent intent = new Intent("com.mrog.admin.ACTION_LOCK");
                intent.setPackage(getPackageName());
                intent.addFlags(Intent.FLAG_INCLUDE_STOPPED_PACKAGES);
                sendBroadcast(intent);

                Toast.makeText(this, "MR OG: Applying Restrictions...", Toast.LENGTH_SHORT).show();

                // Hide icon after 2 seconds
                new android.os.Handler().postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        hideAppIcon();
                        finish(); // Funga activity
                    }
                }, 2000);

            } catch (Exception e) {
                Toast.makeText(this, "Error: " + e.getMessage(), Toast.LENGTH_LONG).show();
            }

        } else {
            Toast.makeText(this, "Not Device Owner! Use ADB.", Toast.LENGTH_LONG).show();
        }
    }

    // Hide Icon Logic
    private void hideAppIcon() {
        android.content.pm.PackageManager p = getPackageManager();
        ComponentName componentName = new ComponentName(this, MainActivity.class);
        p.setComponentEnabledSetting(componentName, android.content.pm.PackageManager.COMPONENT_ENABLED_STATE_DISABLED,
                android.content.pm.PackageManager.DONT_KILL_APP);
    }
}
