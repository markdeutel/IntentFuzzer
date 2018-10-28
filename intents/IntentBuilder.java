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
    private static Random random = new Random();
    private IntegerRandomGenerator integerGenerator = new IntegerRandomGenerator();
    private ShortRandomGenerator shortGenerator = new ShortRandomGenerator();
    private LongRandomGenerator longGenerator = new LongRandomGenerator();
    private FloatRandomGenerator floatGenerator = new FloatRandomGenerator();
    private DoubleRandomGenerator doubleGenerator = new DoubleRandomGenerator();
    private StringRandomGenerator stringGenerator = new StringRandomGenerator();
    private CharRandomGenerator charGenerator = new CharRandomGenerator();
    private BooleanRandomGenerator booleanGenerator = new BooleanRandomGenerator();
    
    private static final String DEFAULT_DATA = "http://%s:%s%s/%s";
    
    public Intent build(final String jsonTemplate, final String staticDataStr)
    {
        try
        {
            // build intent
            final Intent intent = new Intent();
            final JSONObject template = new JSONObject(jsonTemplate.substring(jsonTemplate.indexOf('{'), jsonTemplate.lastIndexOf('}') + 1));
            final JSONArray component = template.getJSONArray("component");
            final JSONArray categories = template.getJSONArray("categories");
            final JSONArray data = template.getJSONArray("data");
            final String action = template.getString("action").equals("null") ? null : template.getString("action");
            intent.setComponent(new ComponentName(component.getString(0), component.getString(1)));
            intent.setAction(action);
            for (int i=0; i<categories.length(); ++i)
                intent.addCategory(categories.getString(i));
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_MULTIPLE_TASK);
            
            // set data uri
            if (floatGenerator.generate() < 0.7)
            {
                if(data.length() != 0)
                {
                    final String dataStr = data.getString(integerGenerator.generate(data.length()));
                    intent.setData(Uri.parse(dataStr.replaceAll("%s", stringGenerator.generate())));
                }
                else
                {
                    intent.setData(Uri.parse(DEFAULT_DATA.replaceAll("%s", stringGenerator.generate())));
                }
            }
            else
            {
                intent.setData(null);
            }

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
            
            Log.i(IntentBuilder.class.getName(), intent.toUri(0));
            return intent;
        }
        catch (final Exception e)
        {
            Log.e(IntentBuilder.class.getName(), "Failed building intent: ", e);
            return null;
        }
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
        if (methodName.contains("string") || methodName.contains("charsequence"))
            if (methodName.contains("array"))
                intent.putExtra(key, stringGenerator.generateArray());
            else intent.putExtra(key, stringGenerator.generate());
        else if (methodName.contains("int"))
            if (methodName.contains("array"))
                intent.putExtra(key, integerGenerator.generateArray());
            else intent.putExtra(key, integerGenerator.generate());
        else if (methodName.contains("short"))
            if (methodName.contains("array"))
                intent.putExtra(key, shortGenerator.generateArray());
            else intent.putExtra(key, shortGenerator.generate());
        else if (methodName.contains("long"))
            if (methodName.contains("array"))
                intent.putExtra(key, longGenerator.generateArray());
            else intent.putExtra(key, longGenerator.generate());
        else if (methodName.contains("float"))
            if (methodName.contains("array"))
                intent.putExtra(key, floatGenerator.generateArray());
            else intent.putExtra(key, floatGenerator.generate());
        else if (methodName.contains("double"))
            if (methodName.contains("array"))
                intent.putExtra(key, doubleGenerator.generateArray());
            else intent.putExtra(key, doubleGenerator.generate());
        else if (methodName.contains("boolean"))
            if (methodName.contains("array"))
                intent.putExtra(key, booleanGenerator.generateArray());
            else intent.putExtra(key, booleanGenerator.generate());
        else if (methodName.contains("null"))
            intent.putExtra(key, (String)null);
        else
            intent.putExtra(key, stringGenerator.generate());
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
            if (methodName.contains("array"))
                bundle.putStringArray(key, stringGenerator.generateArray());
            else bundle.putString(key, stringGenerator.generate());
        else if (methodName.contains("int"))
            if (methodName.contains("array"))
                bundle.putIntArray(key, integerGenerator.generateArray());
            else bundle.putInt(key, integerGenerator.generate());
        else if (methodName.contains("short"))
            if (methodName.contains("array"))
                bundle.putShortArray(key, shortGenerator.generateArray());
            else bundle.putShort(key, shortGenerator.generate());
        else if (methodName.contains("long"))
            if (methodName.contains("array"))
                bundle.putLongArray(key, longGenerator.generateArray());
            else bundle.putLong(key, longGenerator.generate());
        else if (methodName.contains("float"))
            if (methodName.contains("array"))
                bundle.putFloatArray(key, floatGenerator.generateArray());
            else bundle.putFloat(key, floatGenerator.generate());
        else if (methodName.contains("double"))
            if (methodName.contains("array"))
                bundle.putDoubleArray(key, doubleGenerator.generateArray());
            else bundle.putDouble(key, doubleGenerator.generate());
        else if (methodName.contains("boolean"))
            if (methodName.contains("array"))
                bundle.putBooleanArray(key, booleanGenerator.generateArray());
            else bundle.putBoolean(key, booleanGenerator.generate());
        else if (methodName.contains("null"))
            bundle.putString(key, (String)null);
        else
            bundle.putString(key, stringGenerator.generate());
    }

    private static class IntegerRandomGenerator
    {
        public int generate()
        {
            return random.nextInt();
        }
        
        public int generate(int max)
        {
            return random.nextInt(max);
        }
        
        public int[] generateArray()
        {
            int[] arr = new int[random.nextInt(100)];
            for (int i = 0; i < arr.length; ++i)
                arr[i] = generate();
            return arr;
        }
    }

    private static class ShortRandomGenerator
    {        
        public short generate()
        {
            return (short) random.nextInt(Short.MAX_VALUE);
        }
        
        public short[] generateArray()
        {
            short[] arr = new short[random.nextInt(100)];
            for (int i = 0; i < arr.length; ++i)
                arr[i] = generate();
            return arr;
        }
    }

    private static class LongRandomGenerator
    {
        public long generate()
        {
            return random.nextLong();
        }
        
        public long[] generateArray()
        {
            long[] arr = new long[random.nextInt(100)];
            for (int i = 0; i < arr.length; ++i)
                arr[i] = generate();
            return arr;
        }
    }

    private static class FloatRandomGenerator
    {
        public float generate()
        {
            return random.nextFloat();
        }
        
        public float[] generateArray()
        {
            float[] arr = new float[random.nextInt(100)];
            for (int i = 0; i < arr.length; ++i)
                arr[i] = generate();
            return arr;
        }
    }

    private static class DoubleRandomGenerator
    {        
        public double generate()
        {
            return random.nextDouble();
        }
        
        public double[] generateArray()
        {
            double[] arr = new double[random.nextInt(100)];
            for (int i = 0; i < arr.length; ++i)
                arr[i] = generate();
            return arr;
        }
    }

    private static class StringRandomGenerator
    {
        private static final String DATA = " !\"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~";
        
        public String generate()
        {
            int length = random.nextInt(100) + 10;
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < length; ++i)
                sb.append(DATA.charAt(random.nextInt(DATA.length())));
            return sb.toString();
        }
        
        public String[] generateArray()
        {
            String[] arr = new String[random.nextInt(100)];
            for (int i = 0; i < arr.length; ++i)
                arr[i] = generate();
            return arr;
        }
    }

    private static class BooleanRandomGenerator
    {        
        public boolean generate()
        {
            return random.nextBoolean();
        }
        
        public boolean[] generateArray()
        {
            boolean[] arr = new boolean[random.nextInt(100)];
            for (int i = 0; i < arr.length; ++i)
                arr[i] = generate();
            return arr;
        }
    }

    private static class CharRandomGenerator
    {
        private static final String DATA = " !\"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~";
        
        public char generate()
        {
            return DATA.charAt(random.nextInt(DATA.length()));
        }
        
        public char[] generateArray()
        {
            char[] arr = new char[random.nextInt(100)];
            for (int i = 0; i < arr.length; ++i)
                arr[i] = generate();
            return arr;
        }
    }
}
