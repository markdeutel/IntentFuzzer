import java.util.Random;
import android.content.Intent;
import android.content.ComponentName;
import android.os.Bundle;

public class IntentBuilder
{
    private Random random = new Random();
    private Intent intent = null;
    private Bundle bundle = null;
    
    public void createIntent(final String pkg, final String cls)
    {
        intent = new Intent();
        intent.setComponent(new ComponentName(pkg, cls));
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_MULTIPLE_TASK);
    }
    
    public void putExtra(final String extraType, final String key, final String value)
    {
        final String[] extraTypeTokens = extraType.split("\\s+");
        if (extraTypeTokens.length <= 0)
            return;
        
        String[] values = null;
        final boolean isArray = extraTypeTokens.length == 2;
        if(isArray)
            values = value.split("\\s+");
        
        switch(extraTypeTokens[0])
        {
            case "integer":
                if(isArray)
                {
                    int intValues[] = new int[values.length];
                    for(int i=0; i<values.length; ++i)
                        intValues[i] = Integer.parseInt(values[i]);
                    intent.putExtra(key, intValues);
                }
                else
                {
                    intent.putExtra(key, Integer.parseInt(value));
                }
                break;
            case "long":
                if(isArray)
                {
                    long longValues[] = new long[values.length];
                    for(int i=0; i<values.length; ++i)
                        longValues[i] = Long.parseLong(values[i]);
                    intent.putExtra(key, longValues);
                }
                else
                {
                    intent.putExtra(key, Long.parseLong(value));
                }
                break;
            case "short":
                if(isArray)
                {
                    short shortValues[] = new short[values.length];
                    for(int i=0; i<values.length; ++i)
                        shortValues[i] = Short.parseShort(values[i]);
                    intent.putExtra(key, shortValues);
                }
                else
                {
                    intent.putExtra(key, Short.parseShort(value));
                }
                break;
            case "string":
                if(isArray)
                    intent.putExtra(key, values);
                else
                    intent.putExtra(key, value);
                break;
            case "char":
                if(isArray)
                {
                    char charValues[] = new char[values.length];
                    for(int i=0; i<values.length; ++i)
                        charValues[i] = values[i].charAt(random.nextInt(values[i].length()));
                    intent.putExtra(key, charValues);
                }
                else
                {
                    intent.putExtra(key, value.charAt(random.nextInt(value.length())));
                }
                break;
            case "byte":
                if(isArray)
                {
                    byte byteValues[] = new byte[values.length];
                    for(int i=0; i<values.length; ++i)
                    {
                        byte[] bytes = values[i].getBytes();
                        byteValues[i] = bytes[random.nextInt(bytes.length)];
                    }
                    intent.putExtra(key, byteValues);
                }
                else
                {
                    byte[] bytes = value.getBytes();
                    intent.putExtra(key, bytes[random.nextInt(bytes.length)]);
                }
                break;
            case "boolean":
                if(isArray)
                {
                    boolean boolArray[] = new boolean[random.nextInt(100) + 1];
                    for(int i=0; i<boolArray.length; ++i)
                        boolArray[i] = random.nextBoolean();
                    intent.putExtra(key, boolArray);
                }
                else
                {
                    intent.putExtra(key, random.nextBoolean());
                }
                break;
            case "float":
                if(isArray)
                {
                    float floatArray[] = new float[random.nextInt(100) + 1];
                    for(int i=0; i<floatArray.length; ++i)
                        floatArray[i] = Float.parseFloat(values[i]);
                    intent.putExtra(key, floatArray);
                }
                else
                {
                    intent.putExtra(key, Float.parseFloat(value));
                }
                break;
            case "double":
                if(isArray)
                {
                    double doubleArray[] = new double[random.nextInt(100) + 1];
                    for(int i=0; i<doubleArray.length; ++i)
                        doubleArray[i] = Double.parseDouble(values[i]);
                    intent.putExtra(key, doubleArray);
                }
                else
                {
                    intent.putExtra(key, Double.parseDouble(value));
                }
                break;
            default:
                break;
        }
    }
    
    public void createBundle()
    {
        bundle = new Bundle();
    }
    
    public void putBundleExtra(final String extraType, final String key, final String value)
    {
        final String[] extraTypeTokens = extraType.split("\\s+");
        if (extraTypeTokens.length == 0)
            return;
        
        final boolean isArray = extraTypeTokens.length == 2;
        
        switch(extraTypeTokens[0])
        {
            case "integer":
                bundle.putInt(key, Integer.parseInt(value));
                break;
            case "long":
                bundle.putLong(key, Long.parseLong(value));
                break;
            case "short":
                bundle.putShort(key, Short.parseShort(value));
                break;
            case "string":
                bundle.putString(key, value);
                break;
            case "char":
                bundle.putChar(key, value.charAt(random.nextInt(value.length())));
                break;
            case "byte":
                byte[] bytes = value.getBytes();
                bundle.putByte(key, bytes[random.nextInt(bytes.length)]);
                break;
            case "boolean":
                bundle.putBoolean(key, random.nextBoolean());
                break;
            case "float":
                bundle.putFloat(key, Float.parseFloat(value));
                break;
            case "double":
                bundle.putDouble(key, Double.parseDouble(value));
                break;
            default:
                break;
        }
    }
        
    public void applyBundleToIntent()
    {
        intent.putExtras(bundle);
    }
    
    public Intent getIntent()
    {
        return intent;
    }
}
