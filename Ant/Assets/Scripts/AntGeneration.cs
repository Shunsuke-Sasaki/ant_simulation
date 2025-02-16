using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AntGeneration : MonoBehaviour
{
    [SerializeField]
    public float span = 3.0f;
    public int sensitive = 55; //敏感アリの数
    public int insensitive = 5; //鈍感アリの数
    public float sensitivityHigh = 0.90f;
    public float sensitivityLow = 0.4f;

    private float currentTime = 3.0f;
    private int counts = 0;
    private int counti = 0;

    private string Ant1tag = "Ant1";
    private string Ant2tag = "Ant2";

    [Header("References"), SerializeField] private AntController prefab = null;
    private AntController Prefab => prefab;

    [Header("debug"),Multiline(7)] public string debugText = "No Data";

    void FixedUpdate() {
        
        currentTime += Time.deltaTime;
        if(currentTime >= span) {
            counts = GameObject.FindGameObjectsWithTag(Ant1tag).Length;
            counti = GameObject.FindGameObjectsWithTag(Ant2tag).Length;
            if(counts < sensitive) { //敏感アリの数が下回っていたら、敏感アリを生成する
                GenerateAnt(sensitivityHigh, Ant1tag);
            }
            if(counti < insensitive) { //鈍感アリの数が下回っていたら、鈍感アリを生成する
                GenerateAnt(sensitivityLow, Ant2tag);
            }
            currentTime = 0.0f;
        }
        debugText = $"time = {currentTime}\n"
                    +$"sensitive = {counts}\n"
                    +$"insensitive = {counti}";
    }

    private void GenerateAnt(float sensitivity, string tag) {
        var ant = Instantiate(Prefab, transform.position, Quaternion.identity);
        ant.gameObject.SetActive(true);
        ant.Sensitivity = sensitivity;
        ant.tag = tag;
    }
}
