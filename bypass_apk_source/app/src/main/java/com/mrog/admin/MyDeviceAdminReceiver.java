package com.mrog.admin;

import android.app.admin.DeviceAdminReceiver;
import android.app.admin.DevicePolicyManager;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.os.UserManager;
import android.widget.Toast;

public class MyDeviceAdminReceiver extends DeviceAdminReceiver {

    private static final String ACTION_LOCK = "com.mrog.admin.ACTION_LOCK";

    // Orodha ya maadui (KG/MDM Agents) ya kushughulikia
    private static final String[] AGENTS_TO_KILL = {
            "com.samsung.android.kgclient",
            "com.samsung.android.kgclient.agent",
            "com.sec.enterprise.knox.cloudmdm.smdms",
            "com.samsung.klmsagent",
            "com.sec.android.soagent",
            "com.wssyncmldm",
            "com.samsung.android.mdm",
            "com.sec.android.app.samsungapps" // Galaxy Store (Source of updates)
    };

    @Override
    public void onReceive(Context context, Intent intent) {
        if (ACTION_LOCK.equals(intent.getAction())) {
            // Pokea amri ya kuongeza ulinzi (Nuclear Option)
            applyStrongRestrictions(context);
        }
        super.onReceive(context, intent);
    }

    private void applyStrongRestrictions(Context context) {
        DevicePolicyManager dpm = (DevicePolicyManager) context.getSystemService(Context.DEVICE_POLICY_SERVICE);
        ComponentName admin = new ComponentName(context, MyDeviceAdminReceiver.class);

        if (dpm.isDeviceOwnerApp(context.getPackageName())) {
            try {
                // 1. Zuia Reset na Safe Boot (Hii ni nguvu mpya kwa A15/A16)
                dpm.addUserRestriction(admin, UserManager.DISALLOW_FACTORY_RESET);
                dpm.addUserRestriction(admin, UserManager.DISALLOW_SAFE_BOOT); // Muhimu sana
                dpm.addUserRestriction(admin, UserManager.DISALLOW_ADD_USER);
                dpm.addUserRestriction(admin, UserManager.DISALLOW_MOUNT_PHYSICAL_MEDIA);
                dpm.addUserRestriction(admin, UserManager.DISALLOW_CONFIG_PRIVATE_DNS); // Disallow changing DNS

                // 2. Zuia Uninstall
                dpm.addUserRestriction(admin, UserManager.DISALLOW_UNINSTALL_APPS);

                // 3. (FIX KG) Ficha maadui moja kwa moja kupitia DPM (Hii ni nguvu kuliko ADB)
                for (String pkg : AGENTS_TO_KILL) {
                    try {
                        // setApplicationHidden inafanya kazi kama 'pm hide' lakini inasimamiwa na Admin
                        // Hii ni vigumu sana ku-reverse bila kuondoa Admin
                        dpm.setApplicationHidden(admin, pkg, true);
                    } catch (Exception e) {
                        // Ignore if package not found
                    }
                }

                Toast.makeText(context, "MR OG: MAX PROTECTION ACTIVE", Toast.LENGTH_SHORT).show();

            } catch (Exception e) {
                // Log error silently
            }
        }
    }

    @Override
    public void onEnabled(Context context, Intent intent) {
        super.onEnabled(context, intent);
        Toast.makeText(context, "MR OG Admin: ACTIVE", Toast.LENGTH_SHORT).show();
        // Jaribu kuweka ulinzi mara moja
        applyStrongRestrictions(context);
    }

    @Override
    public void onDisabled(Context context, Intent intent) {
        super.onDisabled(context, intent);
        Toast.makeText(context, "MR OG Admin: DISABLED", Toast.LENGTH_SHORT).show();
    }
}
