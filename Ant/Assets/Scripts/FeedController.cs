using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class FeedController : MonoBehaviour
{
    public float Amount { get; set; }
    private int eatCount;
    private int id = -1;
    private int DetectorLayer { get; set; }

    [Header("debug"),Multiline(3)]public string debugText = "No Data";

    GameObject filelogObject;
    FileLog filelog;

    void Start() {
        DetectorLayer = LayerMask.NameToLayer("Dectector");
        eatCount = 0;
        filelogObject = GameObject.Find("FileLog");
        filelog = filelogObject.GetComponent<FileLog>();
    }

    public void SetAmount(float amount) {
        Amount = amount;
        transform.localScale = new Vector3(Amount / 2.0f, 2.0f, Amount / 2.0f);
        debugText = $"amount = {amount}\neat num = {eatCount}\n";

        if(Amount < 0.0f) {//餌が一定回数食べられたら、餌を削除する
            Destroy(this.gameObject, 0.0f);
        }
    }

    public void AddEatCount(){//餌の食べられた回数を増やす
        eatCount++;
    }

    public void SetId(int id){
        this.id = id;
    }

    public void OutputToLog(){
        filelog.WriteFeedData(id,eatCount,Time.frameCount);
    }
}
