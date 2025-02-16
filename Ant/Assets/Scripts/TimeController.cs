using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class TimeController : MonoBehaviour
{
    Slider timeSlider;

    // Use this for initialization
    void Start()
    {
        timeSlider = GetComponent<Slider>();
        timeSlider.maxValue = 4.0f;
        timeSlider.value = 2.0f;
        Time.timeScale = timeSlider.value;
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void OnValueChange()
    {
        Time.timeScale = timeSlider.value;
    }
}
