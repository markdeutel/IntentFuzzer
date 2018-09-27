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
    private IntegerRandomGenerator integerGenerator = new IntegerRandomGenerator(random);
    private ShortRandomGenerator shortGenerator = new ShortRandomGenerator(random);
    private LongRandomGenerator longGenerator = new LongRandomGenerator(random);
    private FloatRandomGenerator floatGenerator = new FloatRandomGenerator(random);
    private DoubleRandomGenerator doubleGenerator = new DoubleRandomGenerator(random);
    private StringRandomGenerator stringGenerator = new StringRandomGenerator(random);
    private CharRandomGenerator charGenerator = new CharRandomGenerator(random);
    private BooleanRandomGenerator booleanGenerator = new BooleanRandomGenerator(random);
    
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

            // add uri
            if (data.length() != 0)
            {
                final String dataTemplate = data.getString(random.nextInt(data.length()));
                intent.setData(Uri.parse(dataTemplate.replaceAll("%s", stringGenerator.generate())));
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
            
            return intent;
        }
        catch (final JSONException e)
        {
            Log.e(IntentBuilder.class.getName(), "Failed parsing data string: ", e);
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
                intent.putExtra(key, stringGenerator.generateArray(new String[random.nextInt(100)]));
            else intent.putExtra(key, stringGenerator.generate());
        else if (methodName.contains("int"))
            if (methodName.contains("array"))
                intent.putExtra(key, integerGenerator.generateArray(new Integer[random.nextInt(100)]));
            else intent.putExtra(key, integerGenerator.generate());
        else if (methodName.contains("short"))
            if (methodName.contains("array"))
                intent.putExtra(key, shortGenerator.generateArray(new Short[random.nextInt(100)]));
            else intent.putExtra(key, shortGenerator.generate());
        else if (methodName.contains("long"))
            if (methodName.contains("array"))
                intent.putExtra(key, longGenerator.generateArray(new Long[random.nextInt(100)]));
            else intent.putExtra(key, longGenerator.generate());
        else if (methodName.contains("float"))
            if (methodName.contains("array"))
                intent.putExtra(key, floatGenerator.generateArray(new Float[random.nextInt(100)]));
            else intent.putExtra(key, floatGenerator.generate());
        else if (methodName.contains("double"))
            if (methodName.contains("array"))
                intent.putExtra(key, doubleGenerator.generateArray(new Double[random.nextInt(100)]));
            else intent.putExtra(key, doubleGenerator.generate());
        else if (methodName.contains("boolean"))
            if (methodName.contains("array"))
                intent.putExtra(key, booleanGenerator.generateArray(new Boolean[random.nextInt(100)]));
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
            bundle.putString(key, stringGenerator.generate());
        else if (methodName.contains("int"))
            bundle.putInt(key, integerGenerator.generate());
        else if (methodName.contains("short"))
            bundle.putShort(key, shortGenerator.generate());
        else if (methodName.contains("long"))
            bundle.putLong(key, longGenerator.generate());
        else if (methodName.contains("float"))
            bundle.putFloat(key, floatGenerator.generate());
        else if (methodName.contains("double"))
            bundle.putDouble(key, doubleGenerator.generate());
        else if (methodName.contains("boolean"))
            bundle.putBoolean(key, booleanGenerator.generate());
        else if (methodName.contains("null"))
            bundle.putString(key, (String)null);
        else
            bundle.putString(key, stringGenerator.generate());
    }

    private static abstract class RandomGenerator<T>
    {
        private static final Integer MAX_LEN = 100;
        protected final Random random;

        public RandomGenerator(Random random)
        {
            this.random = random;
        }

        public abstract T generate();
        
        public T[] generateArray(T[] arr)
        {
            for (int i = 0; i < arr.length; ++i)
                arr[i] = generate();
            return arr;
        }

        public List<T> generateList()
        {
            int size = random.nextInt(MAX_LEN);
            List<T> result = new ArrayList<>(size);
            for (int i = 0; i < size; ++i)
                result.add(generate());
            return result;
        }
    }

    private static class IntegerRandomGenerator extends RandomGenerator<Integer>
    {
        public IntegerRandomGenerator(Random random)
        {
            super(random);
        }
        
        @Override
        public Integer generate()
        {
            return random.nextInt();
        }
    }

    private static class ShortRandomGenerator extends RandomGenerator<Short>
    {
        public ShortRandomGenerator(Random random)
        {
            super(random);
        }
        
        @Override
        public Short generate()
        {
            return (short) random.nextInt(Short.MAX_VALUE);
        }
    }

    private static class LongRandomGenerator extends RandomGenerator<Long>
    {
        public LongRandomGenerator(Random random)
        {
            super(random);
        }

        @Override
        public Long generate()
        {
            return random.nextLong();
        }
    }

    private static class FloatRandomGenerator extends RandomGenerator<Float>
    {
        public FloatRandomGenerator(Random random)
        {
            super(random);
        }
        
        @Override
        public Float generate()
        {
            return random.nextFloat();
        }
    }

    private static class DoubleRandomGenerator extends RandomGenerator<Double>
    {
        public DoubleRandomGenerator(Random random)
        {
            super(random);
        }
        
        @Override
        public Double generate()
        {
            return random.nextDouble();
        }
    }

    private static class StringRandomGenerator extends RandomGenerator<String>
    {
        private static final String DATA = " !\"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~";
        
        public StringRandomGenerator(Random random)
        {
            super(random);
        }
        
        @Override
        public String generate()
        {
            int length = random.nextInt(100) + 10;
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < length; ++i)
                sb.append(DATA.charAt(random.nextInt(DATA.length())));
            return sb.toString();
        }
    }

    private static class BooleanRandomGenerator extends RandomGenerator<Boolean>
    {
        public BooleanRandomGenerator(Random random)
        {
            super(random);
        }
        
        @Override
        public Boolean generate()
        {
            return random.nextBoolean();
        }
    }

    private static class CharRandomGenerator extends RandomGenerator<Character>
    {
        private static final String DATA = " !\"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~";
        
        public CharRandomGenerator(Random random)
        {
            super(random);
        }
        
        @Override
        public Character generate()
        {
            return DATA.charAt(random.nextInt(DATA.length()));
        }
    }
}
