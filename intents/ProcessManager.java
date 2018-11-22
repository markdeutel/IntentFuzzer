import android.content.Context;
import android.content.Intent;
import android.app.ActivityManager;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.util.Log;
import java.util.List;

public class ProcessManager
{
    public void killBackgroundProcess(final Context context, final String packageName)
    {
        final ActivityManager activityManager = (ActivityManager) context.getSystemService(Context.ACTIVITY_SERVICE);
        if (activityManager != null)
        {
            activityManager.killBackgroundProcesses(packageName);
        }
    }
    
    public void sendIntent(final Context context, final String type, final Intent intent)
    {
        switch(type)
        {
            case "activity":
                context.startActivity(intent);
                break;
            case "service":
                context.startService(intent);
                break;
            case "receiver":
                context.sendBroadcast(intent);
                break;
           }
    }
}
