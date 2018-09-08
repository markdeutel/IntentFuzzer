import android.content.Intent;
import android.content.ComponentName;
import android.os.Bundle;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import android.util.Log;
import java.util.List;
import java.util.ArrayList;

public class IntentBuilder
{
    public static Intent build(final String pkg, final String cls, final String dataStr, final String valueStr)
    {
        try
        {
            // build intent
            final Intent intent = new Intent();
            intent.setComponent(new ComponentName(pkg, cls));
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_MULTIPLE_TASK);
            
            // unpack random values for the intent extras
            //final JSONObject values = new JSONObject(valueStr.substring(dataStr.indexOf('{'), dataStr.lastIndexOf('}') + 1));
            
            // set provided extras
            final JSONObject staticData = new JSONObject(dataStr.substring(dataStr.indexOf('{'), dataStr.lastIndexOf('}') + 1));
            if (staticData.length() != 0)
            {
                final JSONObject intentInvocations = staticData.getJSONObject("intentInvocations");
                final JSONObject bundleInvocations = staticData.getJSONObject("bundleInvocations");
             
                final List<String> bundleNames = new ArrayList<>();
                putIntentExtras(intent, intentInvocations, bundleNames);
                putBundleExtras(intent, bundleInvocations, null);
                for (final String bundleName : bundleNames)
                    putBundleExtras(intent, bundleInvocations, bundleName);
            }
            
            return intent;
        }
        catch (final JSONException e)
        {
            Log.e(IntentBuilder.class.getName(), "Failed parsing data string: ", e);
            return null;
        }
    }
        
    public static String getExtrasString(final Intent intent)
    {
        String result = null;
        final Bundle extras = intent.getExtras();
        if (extras != null && extras.keySet().size() != 0)
        {
            final StringBuilder sb = new StringBuilder();
            sb.append("Intent: ");
            for (String key : extras.keySet()) 
            {
                Object value = extras.get(key);
                sb.append(key).append("=").append(value).append(", ");
            }
            result = sb.toString();
        }
        return result;
    }
        
    private static void putIntentExtras(Intent intent, JSONObject intentInvocations, List<String> bundleNames) throws JSONException
    {
        final JSONArray methods = intentInvocations.names();
        if (methods != null)
        {
            for (int i=0; i<methods.length(); ++i)
            {
                boolean isBundleMethod = false;
                final String methodName = methods.getString(i);
                if (methodName.equals("getBundleExtra"))
                    isBundleMethod = true;
                
                final JSONArray keys = intentInvocations.getJSONArray(methodName);
                for (int j=0; j<keys.length(); ++j)
                {
                    final String key = keys.getString(j);
                    if (!key.isEmpty())
                    {
                        if (isBundleMethod)
                            bundleNames.add(key);
                        else
                            intent.putExtra(key, "dummydummytesttest");
                    }
                }
            }
        }
    }
            
    private static void putBundleExtras(Intent intent, JSONObject bundleInvocations, String bundleName) throws JSONException
    {
        final Bundle bundle = new Bundle();
        final JSONArray methods = bundleInvocations.names();
        if (methods != null)
        {
            for (int i=0; i<methods.length(); ++i)
            {
                final JSONArray keys = bundleInvocations.getJSONArray(methods.getString(i));
                for (int j=0; j<keys.length(); ++j)
                {
                    final String key = keys.getString(j);
                    if (!key.isEmpty())
                        bundle.putString(key, "dummydummytesttest");
                }
            }
        }
            
        if (bundleName == null)
            intent.putExtras(bundle);
        else
            intent.putExtra(bundleName, bundle);
    }
}
