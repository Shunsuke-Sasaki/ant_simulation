using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Limitation : MonoBehaviour
{
    private int count;
    public bool flg = true;
    public int limit = 500;

    public string debugText = "No Data";

    void FixedUpdate()
    {
        count = GameObject.FindGameObjectsWithTag("ColonyPheromone").Length + GameObject.FindGameObjectsWithTag("FeedPheromone").Length;
        if (count > limit) flg = false;
        else flg = true;
        debugText = $"pheromone count = {count}";
    }
}
