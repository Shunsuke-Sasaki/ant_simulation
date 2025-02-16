using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PheromoneController : MonoBehaviour
{
    [Header("Settings"), SerializeField] private float updateSpan = 0.1f;
    private float UpdateSpan => updateSpan;

    [SerializeField] private float pheromone = 1.0f;
    public float Pheromone {
        get { return pheromone; }
        set {
            pheromone = value;
        }
    }

    [SerializeField] private float alpha = 0.95f;
    public float Alpha { get { return alpha; } set { alpha = value; } }

    [SerializeField] private float threshold = 0.03f;
    public float Threshold => threshold;

    private float CurrentTime { get; set; }

    void FixedUpdate() {
        CurrentTime += Time.deltaTime;
        if(CurrentTime > UpdateSpan) {
            Pheromone *= Alpha;
            if(Pheromone < Threshold) {//排出されてから時間の経過したフェロモンを削除する
                Destroy(gameObject, 0.0f);
            }
            CurrentTime = 0.0f;
        }
    }

    void OnTriggerEnter(Collider collider) {
        if(collider.gameObject.layer == LayerMask.NameToLayer("Obstacle")) {//障害物とフェロモンが重なっているとき
            Debug.Log("collision!");
            Destroy(this.gameObject, 0.0f);//障害物に重なっているフェロモンを削除する
        }
    }
}
