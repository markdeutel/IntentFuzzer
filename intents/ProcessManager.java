import android.content.Context;
import android.content.Intent;
import android.app.ActivityManager;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.util.Log;
import java.util.List;

public class ProcessManager
{
    public void killBackgroundProcess(final Context context, final String packageName) throws InterruptedException
    {        
        final ActivityManager activityManager = (ActivityManager) context.getSystemService(Context.ACTIVITY_SERVICE);
        if (activityManager != null)
        {
            final List<ActivityManager.RunningTaskInfo> recentTasks = activityManager.getRunningTasks(Integer.MAX_VALUE);
            for (int i = 0; i < recentTasks.size(); i++)
            {
                if (recentTasks.get(i).baseActivity.toShortString().contains("com.mwr.dz"))
                {
                    activityManager.moveTaskToFront(recentTasks.get(i).id, 0);
                    break;
                }    
            }
            activityManager.killBackgroundProcesses(packageName);
            
            Thread.sleep(1000);
        }
    }
    
    public void sendIntent(final Context context, final String type, final Intent intent) throws InterruptedException
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
        
        Thread.sleep(1000);
    }
}
