using UnityEngine;

public static class UnityExtensions
{
    public static float GetPitch(this Vector3 v)
    {
        float len = Mathf.Sqrt((v.x * v.x) + (v.z * v.z));    // Length on xz plane.
        return (-Mathf.Atan2(v.y, len));
    }

    public static float GetYaw(this Vector3 v)
    {
        return (Mathf.Atan2(v.x, v.z));
    }
}
