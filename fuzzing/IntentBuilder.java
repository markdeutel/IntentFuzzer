import java.util.Random;
import android.content.Intent;
import android.content.ComponentName;
import android.os.Bundle;

public class IntentBuilder
{
    private RandomGenerator random = new RandomGenerator();
    private Intent intent = null;
    private Bundle bundle = null;
    
    public void createIntent(final String pkg, final String cls)
    {
        intent = new Intent();
        intent.setComponent(new ComponentName(pkg, cls));
    }
    
    public void putExtra(final String extraType, final String key)
    {
        final String[] extraTypeTokens = extraType.split("\\s+");
        if (extraTypeTokens.length == 0)
            return;
        
        final boolean isArray = extraTypeTokens.length == 2;
        
        switch(extraTypeTokens[0])
        {
            case "boolean":
                if(isArray)
                    intent.putExtra(key, random.getBooleanArray());
                else
                    intent.putExtra(key, random.getBoolean());
                break;
            case "char":
                if(isArray)
                    intent.putExtra(key, random.getCharArray());
                else
                    intent.putExtra(key, random.getChar());
                break;
            case "double":
                if(isArray)
                    intent.putExtra(key, random.getDoubleArray());
                else
                    intent.putExtra(key, random.getDouble());
                break;
            case "float":
                if(isArray)
                    intent.putExtra(key, random.getFloatArray());
                else
                    intent.putExtra(key, random.getFloat());
                break;
            case "integer":
                if(isArray)
                    intent.putExtra(key, random.getIntArray());
                else
                    intent.putExtra(key, random.getInt());
                break;
            case "long":
                if(isArray)
                    intent.putExtra(key, random.getLongArray());
                else
                    intent.putExtra(key, random.getLong());
                break;
            case "short":
                if(isArray)
                    intent.putExtra(key, random.getShortArray());
                else
                    intent.putExtra(key, random.getShort());
                break;
            case "string":
                if(isArray)
                    intent.putExtra(key, random.getStringArray());
                else
                    intent.putExtra(key, random.getString());
                break;
            default:
                break;
        }
    }
    
    public void createBundle()
    {
        bundle = new Bundle();
    }
    
    public void putBundleExtra(final String extraType, final String key)
    {
        final String[] extraTypeTokens = extraType.split("\\s+");
        if (extraTypeTokens.length == 0)
            return;
        
        final boolean isArray = extraTypeTokens.length == 2;
        
        switch(extraTypeTokens[0])
        {
            case "boolean":
                if(isArray)
                    bundle.putBooleanArray(key, random.getBooleanArray());
                else
                    bundle.putBoolean(key, random.getBoolean());
                break;
            case "char":
                if(isArray)
                    bundle.putCharArray(key, random.getCharArray());
                else
                    bundle.putChar(key, random.getChar());
                break;
            case "double":
                if(isArray)
                    bundle.putDoubleArray(key, random.getDoubleArray());
                else
                    bundle.putDouble(key, random.getDouble());
                break;
            case "float":
                if(isArray)
                    bundle.putFloatArray(key, random.getFloatArray());
                else
                    bundle.putFloat(key, random.getFloat());
                break;
            case "integer":
                if(isArray)
                    bundle.putIntArray(key, random.getIntArray());
                else
                    bundle.putInt(key, random.getInt());
                break;
            case "long":
                if(isArray)
                    bundle.putLongArray(key, random.getLongArray());
                else
                    bundle.putLong(key, random.getLong());
                break;
            case "short":
                if(isArray)
                    bundle.putShortArray(key, random.getShortArray());
                else
                    bundle.putShort(key, random.getShort());
                break;
            case "string":
                if(isArray)
                    bundle.putStringArray(key, random.getStringArray());
                else
                    bundle.putString(key, random.getString());
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
        
    public class RandomGenerator
    {
        private static final String ASCII = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
        private Random random = new Random();
        
        public int getInt()
        {
            return random.nextInt();
        }
        
        public short getShort()
        {
            return (short)random.nextInt(Short.MAX_VALUE + 1);
        }
        
        public long getLong()
        {
            return random.nextLong();
        }
        
        public char getChar()
        {
            return ASCII.charAt(random.nextInt(ASCII.length()));
        }
        
        public String getString()
        {
            int len = 1 + random.nextInt(100);
            final StringBuilder sb = new StringBuilder();
            for (int i=0; i<len; ++i)
            {
                sb.append(getChar());
            }
            return sb.toString();
        }
        
        public boolean getBoolean()
        {
            return random.nextBoolean();
        }
        
        public float getFloat()
        {
            return random.nextFloat();
        }
        
        public double getDouble()
        {
            return random.nextDouble();
        }
        
        public int[] getIntArray()
        {
            int len = 1 + random.nextInt(100);
            int[] array = new int[len];
            for (int i=0; i<len; ++i)
                array[i] = getInt();
            return array;
        }
        
        public short[] getShortArray()
        {
            int len = 1 + random.nextInt(100);
            short[] array = new short[len];
            for (int i=0; i<len; ++i)
                array[i] = getShort();
            return array;
        }
        
        public long[] getLongArray()
        {
            int len = 1 + random.nextInt(100);
            long[] array = new long[len];
            for (int i=0; i<len; ++i)
                array[i] = getLong();
            return array;
        }
        
        public char[] getCharArray()
        {
            int len = 1 + random.nextInt(100);
            char[] array = new char[len];
            for (int i=0; i<len; ++i)
                array[i] = getChar();
            return array;
        }
        
        public String[] getStringArray()
        {
            int len = 1 + random.nextInt(100);
            String[] array = new String[len];
            for (int i=0; i<len; ++i)
                array[i] = getString();
            return array;
        }
        
        public boolean[] getBooleanArray()
        {
            int len = 1 + random.nextInt(100);
            boolean[] array = new boolean[len];
            for (int i=0; i<len; ++i)
                array[i] = getBoolean();
            return array;
        }
        
        public float[] getFloatArray()
        {
            int len = 1 + random.nextInt(100);
            float[] array = new float[len];
            for (int i=0; i<len; ++i)
                array[i] = getFloat();
            return array;
        }
        
        public double[] getDoubleArray()
        {
            int len = 1 + random.nextInt(100);
            double[] array = new double[len];
            for (int i=0; i<len; ++i)
                array[i] = getDouble();
            return array;
        }
    }
}
