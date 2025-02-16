using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;

[Serializable]
public class PheromoneInfo
{
    [SerializeField] private float alpha = 0.1f;
    public float Alpha => alpha;

    [SerializeField] private float r = 1.0f;
    public float R => r;

    [SerializeField] private string layerName = "ColonyPheromone";
    private string LayerName => layerName;

    [SerializeField] private int threshold = 1;
    public int Threshold => threshold;

    public int Count { get; set; }
    public Vector3 Direction { get; set; }
    public int Layer { get { return LayerMask.NameToLayer(LayerName); } }

    public void NormalizeDirection() {
        Direction = Direction.normalized;
    }

    public void Reset() {
        Count = 0;
        Direction = Vector3.zero;
    }
}
