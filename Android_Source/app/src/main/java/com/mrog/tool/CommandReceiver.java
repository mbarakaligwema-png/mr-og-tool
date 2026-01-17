package com.mrog.tool;

import android.app.admin.DevicePolicyManager;
import android.content.BroadcastReceiver;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.os.UserManager;
import android.util.Log;
import android.widget.Toast;
import android.provider.Settings;

public class CommandReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        if ("com.mrog.tool.ACTION_LOCK".equals(intent.getAction())) {
            Log.d("MROG", "Received LOCK command");
            DevicePolicyManager dpm = (DevicePolicyManager) context.getSystemService(Context.DEVICE_POLICY_SERVICE);
            ComponentName adminName = new ComponentName(context, MyDeviceAdminReceiver.class);

            if (dpm.isDeviceOwnerApp(context.getPackageName())) {
                try {
                    // Re-apply Critical Restrictions
                    String[] restrictions = {
                            UserManager.DISALLOW_FACTORY_RESET,
                            UserManager.DISALLOW_ADD_USER,
                            UserManager.DISALLOW_REMOVE_USER,
                            UserManager.DISALLOW_SMS,
                            UserManager.DISALLOW_CONFIG_VPN,
                            UserManager.DISALLOW_CONFIG_TETHERING,
                            "no_config_private_dns",
                            "disallow_config_private_dns"
                    };

                    for (String r : restrictions) {
                        try {
                            dpm.addUserRestriction(adminName, r);
                        } catch (Exception e) {
                            Log.e("MROG", "Failed to set: " + r);
                        }
                    }

                    // NEW: Also Hide Apps on Lock Command
                    String[] hideApps = {
                            "com.sec.android.app.factoryreset",
                            "com.android.settings.FactoryResetActivity",
                            "com.samsung.android.settings.intelligence",
                            "com.sec.android.easyMover"
                    };
                    for (String app : hideApps) {
                        try {
                            dpm.setApplicationHidden(adminName, app, true);
                        } catch (Exception e) {
                        }
                    }

                    // Force refresh setup wizard state to prevent loop
                    try {
                        Settings.Global.putInt(context.getContentResolver(), Settings.Global.DEVICE_PROVISIONED, 1);
                    } catch (Exception e) {
                    }

                    // Visual Confirmation
                    try {
                        dpm.lockNow(); // Force lock to prove admin control
                    } catch (SecurityException ex) {
                        Log.e("MROG", "Lock failed", ex);
                    }

                    Toast.makeText(context, "MROG: SYSTEM LOCKED & SECURED", Toast.LENGTH_LONG).show();
                } catch (Exception e) {
                    Log.e("MROG", "Error in CommandReceiver", e);
                }
            }
        }
    }
}
