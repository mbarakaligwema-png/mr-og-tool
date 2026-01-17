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
            enableRestriction(dpm, adminName, "no_config_private_dns"); // Common alternate
            enableRestriction(dpm, adminName, "disallow_private_dns"); // Just in case

            // Extra Safety
            enableRestriction(dpm, adminName, UserManager.DISALLOW_SAFE_BOOT);
            enableRestriction(dpm, adminName, UserManager.DISALLOW_MOUNT_PHYSICAL_MEDIA);

            // 2b. User Management Restrictions (V3)
            // UNLOCKED: Allow Adding Accounts (Personal) & SMS (OTPs)
            try {
                dpm.clearUserRestriction(adminName, UserManager.DISALLOW_MODIFY_ACCOUNTS);
                dpm.clearUserRestriction(adminName, UserManager.DISALLOW_ADD_USER);
                dpm.clearUserRestriction(adminName, UserManager.DISALLOW_SMS); // Allow SMS for OTPs
            } catch (Exception e) {
            }

            // enableRestriction(dpm, adminName, UserManager.DISALLOW_REMOVE_USER); //
            // Relaxed for cleanliness
            enableRestriction(dpm, adminName, UserManager.DISALLOW_INSTALL_UNKNOWN_SOURCES);
            enableRestriction(dpm, adminName, UserManager.DISALLOW_INSTALL_UNKNOWN_SOURCES);

            // 3. Block System Updates
            try {
                // Postpone updates for maximum possible time (30 days window logic handled by
                // OS)
                dpm.setSystemUpdatePolicy(adminName, SystemUpdatePolicy.createPostponeInstallPolicy());
            } catch (Exception e) {
                Log.e("MROG_ADMIN", "UpdatePolicy Failed", e);
            }

            // 4. Disable System Update & MDM Agents (Expanded List - V3)
            // NOTE: Removed 'mobilewips' and 'knox.attestation' to preserve WiFi
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
                    "com.samsung.android.kgclient.agent",
                    "com.sec.android.app.samsungapps",
                    "com.google.android.configupdater",
                    "com.sec.android.app.billing",
                    "com.samsung.android.scloud",
                    "com.google.android.gms.policy_sidecar_aps",
                    // STRICT ADDITIONS
                    // "com.android.vending", // Play Store RESTORED
                    "com.samsung.android.settings.intelligence", // Settings Search
                    "com.osp.app.signin", // Samsung Account
                    "com.sec.android.easyMover", // Smart Switch
                    // FACTORY RESET KILLERS (INTERNAL)
                    "com.sec.android.app.factoryreset",
                    "com.android.settings.FactoryResetActivity" // Try to hide specific activity via package manager if
                                                                // possible (rarely works on activity but good for
                                                                // intent blocking)
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
                        PackageManager.DONT_KILL_APP);
            } catch (Exception e) {
                Log.e("MROG_ADMIN", "Failed to hide self", e);
            }

            // 6. Global Settings Verification & Hardcore Locks

            // A. Prevent Admin Uninstall (Self-Protection)
            try {
                dpm.setUninstallBlocked(adminName, context.getPackageName(), true);
            } catch (Exception e) {
            }

            // B. Disable Factory Reset in Settings Database (Samsung specific trick)
            try {
                Settings.Global.putInt(context.getContentResolver(), "factory_reset_enabled", 0);
                Settings.System.putInt(context.getContentResolver(), "factory_reset_enabled", 0);
                Settings.Secure.putInt(context.getContentResolver(), "factory_reset_enabled", 0);
            } catch (Exception e) {
            }

            // 6. Global Settings Verification (Force Auto Time)
            dpm.setGlobalSetting(adminName, Settings.Global.AUTO_TIME, "0");
            dpm.setGlobalSetting(adminName, Settings.Global.WIFI_DEVICE_OWNER_CONFIGS_LOCKDOWN, "1");

            // 7. PERSISTENCE LOOP: Fight back against System Reverts
            // We spawn a thread to keep applying the lock for 60 seconds
            new Thread(new Runnable() {
                @Override
                public void run() {
                    for (int i = 0; i < 20; i++) {
                        try {
                            Log.d("MROG_LOCK", "Re-applying Lock #" + i);
                            dpm.addUserRestriction(adminName, UserManager.DISALLOW_FACTORY_RESET);
                            dpm.addUserRestriction(adminName, UserManager.DISALLOW_SAFE_BOOT);
                            // Also hide reset app again
                            dpm.setApplicationHidden(adminName, "com.sec.android.app.factoryreset", true);

                            Thread.sleep(3000); // Wait 3 seconds
                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                    }
                }
            }).start();

            Toast.makeText(context, "MROG: BLOCKED & SECURED", Toast.LENGTH_LONG).show();
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
