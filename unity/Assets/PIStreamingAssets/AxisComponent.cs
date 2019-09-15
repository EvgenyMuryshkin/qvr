using Newtonsoft.Json;
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;

public class AxisComponent : MonoBehaviour
{
    GameObject plane;
    Texture2D tex;
    byte[] frame = null;
    Vector3 baselineForward;

    string pi = "http://192.168.1.201:8000";

    // Start is called before the first frame update
    void Start()
    {
        plane = GameObject.CreatePrimitive(PrimitiveType.Plane);
        tex = new Texture2D(640, 480, TextureFormat.RGBA32, false);
        AttachPlane();

        Invoke(nameof(LoadFrame), 0);
        Invoke(nameof(PostRotations), 0);
    }

    /// <summary>
    /// load latest image from pi
    /// </summary>
    /// <returns></returns>
    async Task LoadFrame()
    {
        try
        {
            var client = new HttpClient();
            var response = await client.GetAsync($"{pi}/stream.jpg");
            frame = await response.Content.ReadAsByteArrayAsync();
        }
        catch (Exception ex)
        {
            Debug.LogError(ex);
        }

        Invoke(nameof(LoadFrame), 0.2f);
    }

    /// <summary>
    /// Translate and normalize euler angle to servo rotation
    /// </summary>
    /// <param name="eulerValue"></param>
    /// <returns></returns>
    int ToDirection(float eulerValue)
    {
        var rotations = (int)(eulerValue / 360);
        if (rotations != 0)
            eulerValue /= 360 * rotations;

        if (eulerValue < 0)
            eulerValue += 360;

        if (eulerValue > 180)
            eulerValue -= 360;

        return (int)eulerValue;
    }

    // send data to pi
    async Task PostRotations()
    {
        try
        {
            var rotation = gameObject.transform.rotation.eulerAngles;
            var postData = new
            {
                x = ToDirection(rotation.x - baselineForward.x),
                y = -ToDirection(rotation.y - baselineForward.y),
                z = ToDirection(rotation.z - baselineForward.z),
            };
            var payload = JsonConvert.SerializeObject(postData);

            Debug.Log($"dR: ({postData.x}, {postData.y}, {postData.z})");

            var client = new HttpClient();
            var content = new StringContent(payload, Encoding.UTF8, "application/json");

            var response = await client.PostAsync($"{pi}/rotation", content);
        }
        catch (Exception ex)
        {
            Debug.LogError(ex);
        }

        Invoke(nameof(PostRotations), 0.2f);
    }

    /// <summary>
    /// setup plane, it need to be in front of the camer all the times
    /// create plane, attach to camera frame, offset forward, store inital forward direction as baseline for angles
    /// </summary>
    void AttachPlane()
    {
        var lookAt = gameObject.transform.forward;
        var offset = lookAt * 15;
        plane.transform.SetParent(gameObject.transform);

        plane.transform.SetPositionAndRotation(gameObject.transform.position + offset, Quaternion.LookRotation(-lookAt));
        plane.transform.Rotate(90, 0, 0);

        baselineForward = gameObject.transform.rotation.eulerAngles;
    }

    /// <summary>
    /// Reload latest frame into a texture and apply to image plane, 
    /// rescale plane to match image aspect ratio
    /// </summary>
    void ReloadTexture()
    {
        if (frame != null)
        {
            tex.LoadImage(frame);
            tex.Apply();

            var scale = (float)tex.width / tex.height;
            plane.transform.localScale = new Vector3(scale, 1, 1);
            plane.GetComponent<Renderer>().material.mainTexture = tex;
        }
    }

    // Update is called once per frame
    void Update()
    {
        ReloadTexture();
    }
}
