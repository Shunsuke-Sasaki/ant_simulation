using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;
using System;

public class FileLog : MonoBehaviour
{
   private StreamWriter sw;
    void Start()
    {
        DateTime dt = DateTime.Now;
        string path = "../" + dt.ToString("yyyyMMddHHmmss") + "log.txt";
        sw = new StreamWriter(path,false);
    }

    public void WriteFeedData(int id, int count, int frame){
        sw.WriteLine(id + "," + count + "," + frame);
    }


    private void OnApplicationQuit()
    {
        sw.Flush();
        sw.Close();
    }
}
