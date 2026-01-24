package com.mrog.admin;

import android.app.admin.DeviceAdminReceiver;
import android.app.admin.DevicePolicyManager;
import android.app.admin.SystemUpdatePolicy; // IMPORTS
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.os.UserManager;
import android.widget.Toast;

public class MyDeviceAdminReceiver extends DeviceAdminReceiver {
    // MROG TOOL - 2025 CLEAN

    @Override
    public void onEnabled(Context context, Intent intent) {
        super.onEnabled(context, intent);

        DevicePolicyManager dpm = (DevicePolicyManager) context.getSystemService(Context.DEVICE_POLICY_SERVICE);
        ComponentName admin = getWho(context);

        try {
            // Priority 1: DISALLOW_FACTORY_RESET
            dpm.addUserRestriction(admin, UserManager.DISALLOW_FACTORY_RESET);

            // Priority 2: DISALLOW_NETWORK_RESET
            dpm.addUserRestriction(admin, UserManager.DISALLOW_NETWORK_RESET);

            // Priority 3: DNS LEAK BLOCKING (STRICT FORCE)
            // 3a. Force AdGuard DNS (Blocks Samsung Trackers) - API 29+
            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.Q) {
                try {
                    dpm.setGlobalPrivateDnsModeSpecifiedHost(admin, "dns.adguard.com");
                    Toast.makeText(context, "MROG: DNS Forcing AdGuard...", Toast.LENGTH_SHORT).show();
                } catch (Exception e) {
                    // Fallback if API < 29 or fails: Lock Config
                    dpm.addUserRestriction(admin, "no_config_private_dns");
                }
            } else {
                dpm.addUserRestriction(admin, "no_config_private_dns");
            }

            // 3b. VPN (Causes DNS leaks/override)
            dpm.addUserRestriction(admin, UserManager.DISALLOW_CONFIG_VPN);

            // 3c. Mobile Network (APN DNS)
            dpm.addUserRestriction(admin, UserManager.DISALLOW_CONFIG_MOBILE_NETWORKS);

            // 3d. Tethering & Hotspot (Network Sharing)
            dpm.addUserRestriction(admin, UserManager.DISALLOW_CONFIG_TETHERING);
            dpm.addUserRestriction(admin, UserManager.DISALLOW_BLUETOOTH_SHARING);

            // 4. BLOCK UPDATES (System Update Policy) - REMOVED due to Compilation Error
            // Tutaongeza njia nyingine baadaye.

            // 5. NUCLEAR OPTION: Hide KG/MDM Clients via Policy
            // Hii inafanya APK izime hizi apps "Milele"
            String[] enemies = {
                    "com.samsung.android.kgclient",
                    "com.samsung.android.kgclient.agent",
                    "com.sec.enterprise.knox.cloudmdm.smdms",
                    "com.samsung.android.mdm",
                    "com.sec.android.soagent",
                    "com.wssyncmldm",
                    "com.samsung.android.app.updatecenter",
                    "com.sec.android.app.samsungapps" // Galaxy Store
            };

            for (String pkg : enemies) {
                try {
                    // 1. Hide (Ficha)
                    dpm.setApplicationHidden(admin, pkg, true);
                } catch (Exception e) {
                }
            }

            // 2. Suspend (Simamisha kabisa) - API 24+
            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.N) {
                try {
                    dpm.setPackagesSuspended(admin, enemies, true);
                } catch (Exception e) {
                }
            }

            Toast.makeText(context, "MROG: Secured + KG Clients Suspended", Toast.LENGTH_SHORT).show();

        } catch (Exception e) {
            // Silent Fail compatible
        }
    }

    @Override
    public void onDisabled(Context context, Intent intent) {
        super.onDisabled(context, intent);
    }
}
