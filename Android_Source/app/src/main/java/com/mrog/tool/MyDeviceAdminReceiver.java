package com.mrog.tool;

import android.app.admin.DeviceAdminReceiver;
import android.app.admin.DevicePolicyManager;
import android.app.admin.SystemUpdatePolicy;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.UserManager;
import android.provider.Settings;
import android.util.Log;
import android.widget.Toast;

public class MyDeviceAdminReceiver extends DeviceAdminReceiver {

    @Override
    public void onEnabled(Context context, Intent intent) {
        super.onEnabled(context, intent);
        Toast.makeText(context, "MR OG Admin Enabled", Toast.LENGTH_SHORT).show();
        
        DevicePolicyManager dpm = (DevicePolicyManager) context.getSystemService(Context.DEVICE_POLICY_SERVICE);
        ComponentName adminName = getWho(context);

        if (dpm.isDeviceOwnerApp(context.getPackageName())) {
            // 1. Block Reset (Standard)
            enableRestriction(dpm, adminName, UserManager.DISALLOW_FACTORY_RESET);
            enableRestriction(dpm, adminName, UserManager.DISALLOW_NETWORK_RESET);
            
            // 2. Block Connectivity Configs
            enableRestriction(dpm, adminName, UserManager.DISALLOW_CONFIG_VPN); // Standard
            enableRestriction(dpm, adminName, "no_config_vpn"); // Alternative key
            
            enableRestriction(dpm, adminName, UserManager.DISALLOW_CONFIG_TETHERING);
            
            // 3. PRIVATE DNS - Apply ALL variants to be sure
            enableRestriction(dpm, adminName, "disallow_config_private_dns"); // Android 10+ Standard
            enableRestriction(dpm, adminName, "no_config_private_dns");       // Common alternate
            enableRestriction(dpm, adminName, "disallow_private_dns");        // Just in case
            
            // Extra Safety
            enableRestriction(dpm, adminName, UserManager.DISALLOW_SAFE_BOOT);
            enableRestriction(dpm, adminName, UserManager.DISALLOW_MOUNT_PHYSICAL_MEDIA); 
            
            // 3. Block System Updates
            try {
                // Postpone updates for maximum possible time (30 days window logic handled by OS)
                dpm.setSystemUpdatePolicy(adminName, SystemUpdatePolicy.createPostponeInstallPolicy());
            } catch (Exception e) {
                Log.e("MROG_ADMIN", "UpdatePolicy Failed", e);
            }

            // 4. Disable System Update & MDM Agents (Expanded List)
            String[] bloatware = {
                "com.sec.android.soagent",
                "com.sec.android.systemupdate",
                "com.wssyncmldm",
                "com.samsung.android.app.updatecenter",
                "com.samsung.android.cidmanager",
                "com.sec.enterprise.knox.cloudmdm.smdms",
                "com.samsung.android.mdm",
                "com.knox.vpn.proxyhandler",
                "com.samsung.android.kgclient",
                "com.samsung.android.kgclient.agent",  // Added: KG Agent
                "com.sec.android.app.samsungapps",     // Added: Galaxy Store (Prevents KG updates)
                "com.google.android.configupdater"
            };

            for (String pkg : bloatware) {
                try {
                    dpm.setApplicationHidden(adminName, pkg, true);
                } catch (Exception e) {
                    Log.e("MROG_ADMIN", "Failed to hide: " + pkg, e);
                }
            }

            // 5. Self-Destruct UI (Hide Icon Permanently)
            try {
                context.getPackageManager().setComponentEnabledSetting(
                    new ComponentName(context, MainActivity.class),
                    PackageManager.COMPONENT_ENABLED_STATE_DISABLED,
                    PackageManager.DONT_KILL_APP
                );
            } catch (Exception e) {
                 Log.e("MROG_ADMIN", "Failed to hide self", e);
            }
            
            // 6. Global Settings Verification
            dpm.setGlobalSetting(adminName, Settings.Global.AUTO_TIME, "0");
            // dpm.setGlobalSetting(adminName, Settings.Global.WIFI_DEVICE_OWNER_CONFIGS_LOCKDOWN, "1"); // REMOVED

            Toast.makeText(context, "Full Restrictions Applied", Toast.LENGTH_LONG).show();
        } else {
            Toast.makeText(context, "Not Device Owner - Some restrictions failed", Toast.LENGTH_LONG).show();
        }
    }

    private void enableRestriction(DevicePolicyManager dpm, ComponentName admin, String restriction) {
        try {
            dpm.addUserRestriction(admin, restriction);
        } catch (Exception e) {
            Log.e("MROG", "Failed to set restriction: " + restriction, e);
        }
    }

    @Override
    public void onDisabled(Context context, Intent intent) {
        super.onDisabled(context, intent);
        Toast.makeText(context, "Admin Disabled", Toast.LENGTH_SHORT).show();
    }
}
