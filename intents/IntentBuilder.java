import android.content.Intent;
import android.content.ComponentName;
import android.os.Bundle;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import android.util.Log;
import java.util.List;
import java.util.ArrayList;

import java.util.Random;
import java.nio.charset.Charset;

public class IntentBuilder
{
    private Random random = new Random();
    
    public Intent build(final String pkg, final String cls, final String dataStr, final String metaStr)
    {
        try
        {
            // build intent
            final Intent intent = new Intent();
            intent.setComponent(new ComponentName(pkg, cls));
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_MULTIPLE_TASK);
            
            // set provided meta data
            final JSONObject metaData = new JSONObject(metaStr.substring(metaStr.indexOf('{'), metaStr.lastIndexOf('}') + 1));
            if (metaData.length() > 0)
            {
                // set actions
                final JSONArray actions = metaData.getJSONArray("actions");
                final List<String> actionsList = new ArrayList<>();
                for (int i=0; i<actions.length(); ++i)
                    actionsList.add(actions.getString(i));
                if (actionsList.size() > 0)
                    intent.setAction(actionsList.get(random.nextInt(actionsList.size())));
                    
                // set categories
                final JSONArray categories = metaData.getJSONArray("categories");
                final List<String> categoryList = new ArrayList<>();
                for (int i=0; i<categories.length(); ++i)
                    intent.addCategory(categories.getString(i));
                    
                // set data
                final JSONArray data = metaData.getJSONArray("data");
            }

            // set provided extras
            final JSONObject staticData = new JSONObject(dataStr.substring(dataStr.indexOf('{'), dataStr.lastIndexOf('}') + 1));
            if (staticData.length() > 0)
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
        
    public String getExtrasString(final Intent intent)
    {
        String result = null;
        final Bundle extras = intent.getExtras();
        if (extras != null && extras.keySet().size() != 0)
        {
            final StringBuilder sb = new StringBuilder();
            sb.append("Extras: ");
            for (String key : extras.keySet()) 
            {
                sb.append(key).append(", ");
            }
            result = sb.toString();
        }
        return result;
    }
        
    private void putIntentExtras(Intent intent, JSONObject intentInvocations, List<String> bundleNames) throws JSONException
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
                            putTwistedIntentExtra(intent, key);
                    }
                }
            }
        }
    }
            
    private void putBundleExtras(Intent intent, JSONObject bundleInvocations, String bundleName) throws JSONException
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
                        putTwistedBundleExtra(bundle, key);
                }
            }
        }
            
        if (bundleName == null)
            intent.putExtras(bundle);
        else
            intent.putExtra(bundleName, bundle);
    }
                
    private void putTwistedIntentExtra(Intent intent, String key)
    {
        int pick = random.nextInt(4);
        switch(pick)
        {
            case 0: // string
                intent.putExtra(key, nextRandomString());
                break;
            case 1: // integer
                intent.putExtra(key, random.nextInt());
                break;
            case 2: // float
                intent.putExtra(key, random.nextFloat());
                break;
            case 3: // boolean
                intent.putExtra(key, random.nextBoolean());
                break;
        }
    }
        
    private void putTwistedBundleExtra(Bundle bundle, String key)
    {
        int pick = random.nextInt(4);
        switch(pick)
        {
            case 0: // string
                bundle.putString(key, nextRandomString());
                break;
            case 1: // integer
                bundle.putInt(key, random.nextInt());
                break;
            case 2: // float
                bundle.putFloat(key, random.nextFloat());
                break;
            case 3: // boolean
                bundle.putBoolean(key, random.nextBoolean());
                break;
        }
    }
                
    private String nextRandomString()
    {
        int length = random.nextInt(100) + 10;
        byte[] arr = new byte[length];
        random.nextBytes(arr);
        return new String(arr, Charset.forName("UTF-8"));
    }
}
