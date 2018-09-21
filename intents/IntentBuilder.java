import android.content.Intent;
import android.content.ComponentName;
import android.os.Bundle;
import 	android.net.Uri;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import android.util.Log;
import java.util.List;
import java.util.ArrayList;

import java.util.Random;
import java.nio.charset.Charset;

/**
* @author Mark Deutel
*/
public class IntentBuilder
{
    private Random random = new Random();
    
    public Intent build(final String jsonTemplate, final String staticDataStr)
    {
        try
        {
            // build intent
            final Intent intent = new Intent();
            final JSONObject template = new JSONObject(jsonTemplate.substring(jsonTemplate.indexOf('{'), jsonTemplate.lastIndexOf('}') + 1));
            final JSONArray component = template.getJSONArray("component");
            final JSONArray categories = template.getJSONArray("categories");
            final String action = template.getString("action").equals("null") ? null : template.getString("action");
            intent.setComponent(new ComponentName(component.getString(0), component.getString(1)));
            intent.setAction(action);
            for (int i=0; i<categories.length(); ++i)
                intent.addCategory(categories.getString(i));
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_MULTIPLE_TASK);

            // set provided extras
            final JSONObject staticData = new JSONObject(staticDataStr.substring(staticDataStr.indexOf('{'), staticDataStr.lastIndexOf('}') + 1));
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
                            putIntentExtra(intent, methodName, key);
                    }
                }
            }
        }
    }
                    
    private void putIntentExtra(Intent intent, String methodName, String key)
    {
        methodName = methodName.toLowerCase();
        if (methodName.contains("string"))
            intent.putExtra(key, nextRandomString());
        else if (methodName.contains("int"))
            intent.putExtra(key, random.nextInt());
        else if (methodName.contains("short"))
            intent.putExtra(key, (short) random.nextInt(Short.MAX_VALUE + 1));
        else if (methodName.contains("long"))
            intent.putExtra(key, random.nextLong());
        else if (methodName.contains("float"))
            intent.putExtra(key, random.nextFloat());
        else if (methodName.contains("double"))
            intent.putExtra(key, random.nextDouble());
        else if (methodName.contains("boolean"))
            intent.putExtra(key, random.nextBoolean());
        else if (methodName.contains("null"))
            intent.putExtra(key, (String)null);
        else
            intent.putExtra(key, nextRandomString());
    }
            
    private void putBundleExtras(Intent intent, JSONObject bundleInvocations, String bundleName) throws JSONException
    {
        final Bundle bundle = new Bundle();
        final JSONArray methods = bundleInvocations.names();
        if (methods != null)
        {
            for (int i=0; i<methods.length(); ++i)
            {
                final String methodName = methods.getString(i);
                final JSONArray keys = bundleInvocations.getJSONArray(methods.getString(i));
                for (int j=0; j<keys.length(); ++j)
                {
                    final String key = keys.getString(j);
                    if (!key.isEmpty())
                        putBundleExtra(bundle, methodName, key);
                }
            }
        }
            
        if (bundleName == null)
            intent.putExtras(bundle);
        else
            intent.putExtra(bundleName, bundle);
    }
        
    private void putBundleExtra(Bundle bundle, String methodName, String key)
    {
        methodName = methodName.toLowerCase();
        if (methodName.contains("string"))
            bundle.putString(key, nextRandomString());
        else if (methodName.contains("int"))
            bundle.putInt(key, random.nextInt());
        else if (methodName.contains("short"))
            bundle.putShort(key, (short) random.nextInt(Short.MAX_VALUE + 1));
        else if (methodName.contains("long"))
            bundle.putLong(key, random.nextLong());
        else if (methodName.contains("float"))
            bundle.putFloat(key, random.nextFloat());
        else if (methodName.contains("double"))
            bundle.putDouble(key, random.nextDouble());
        else if (methodName.contains("boolean"))
            bundle.putBoolean(key, random.nextBoolean());
        else if (methodName.contains("null"))
            bundle.putString(key, (String)null);
        else
            bundle.putString(key, nextRandomString());
    }
               
    private static final String DATA = " !\"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~";
    private String nextRandomString()
    {
        int length = random.nextInt(100) + 10;
        final StringBuilder sb = new StringBuilder();
        for (int i=0; i<length; ++i)
            sb.append(DATA.charAt(random.nextInt(DATA.length())));
        return sb.toString();
    }
}
