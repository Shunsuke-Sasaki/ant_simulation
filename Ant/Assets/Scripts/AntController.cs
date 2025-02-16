using UnityEngine;
using UnityEngine.AI;

public enum AntState
{
    Random = 0,
    PheromoneSearch,
    BackHome
}

public class AntController : MonoBehaviour
{
    [Header("References"), SerializeField] private PheromoneController pheromonePrefab1 = null;
    private PheromoneController PheromonePrefab1 => pheromonePrefab1;

    [SerializeField] private PheromoneController pheromonePrefab2 = null;
    private PheromoneController PheromonePrefab2 => pheromonePrefab2;

    [SerializeField] private GameObject colony = null;
    private GameObject Colony => colony;

    [SerializeField] private Limitation limitation = null;
    private Limitation Limitation => limitation;

    [SerializeField] private SpriteRenderer antRenderer = null;
    public SpriteRenderer AntRenderer { get { return antRenderer; } }

    [Header("Settings"), SerializeField] private float updateSpan = 0.1f;
    private float UpdateSpan => updateSpan;

    [SerializeField] private int pheromoneStep = 2;
    private int PheromoneStep => pheromoneStep;

    [Header("Parameters"), SerializeField] private float alpha = 0.1f;
    private float Alpha => alpha;

    [SerializeField] private float threshold = 0.01f;
    public float Threshold => threshold;

    public float Sensitivity { get; set; }

    [Header("Pheromone Info"), SerializeField] private PheromoneInfo colonyPheromone = null;
    private PheromoneInfo ColonyPheromone => colonyPheromone;

    [SerializeField] private PheromoneInfo feedPheromone = null;
    private PheromoneInfo FeedPheromone => feedPheromone;

    // gaussian distribution
    private float Z { get; set; }

    public AntState State { get; set; }

    public NavMeshAgent Agent { get; set; }

    private bool DetectFeed { get; set; }
    private Vector3 FeedDirection { get; set; }
    private bool DetectHome { get; set; }
    private Vector3 HomeDirection { get; set; }

    public float E { get; set; } = 1.0f;

    private float Speed { get; set; }
    private Vector3 ColonyPosition { get; set; }

    private float CurrentTime { get; set; }
    private int CurrentPheromoneStep { get; set; }

    public int FeedLayer { get; private set; }
    public int ColonyLayer { get; private set; }

    private AntGeneration antGeneration { get; set; }

    [Header("debug"),Multiline(7)] public string debugText = "No Data";

    void Start() {
        Agent = GetComponent<NavMeshAgent>();
        AntRenderer.color = Color.black;
        transform.Rotate(new Vector3(0, Random.value * 360, 0));

        antGeneration = Colony.GetComponent<AntGeneration>();

        ColonyPosition = transform.position;
        Speed = 35.0f;

        FeedLayer = LayerMask.NameToLayer("Feed");
        ColonyLayer = LayerMask.NameToLayer("Colony");
    }

    void FixedUpdate() {
        CurrentTime += Time.deltaTime;
        if(CurrentTime > UpdateSpan) {
            // フェロモンの方向ベクトルの正規化
            ColonyPheromone.NormalizeDirection();
            FeedPheromone.NormalizeDirection();

            //状態の遷移
            if(State == AntState.Random && FeedPheromone.Count >= FeedPheromone.Threshold){//ランダム探索状態のときに餌フェロモンの数が一定値を上回ったとき
                State = AntState.PheromoneSearch;//フェロモン探索状態に移行
            }
            else if(State == AntState.PheromoneSearch && FeedPheromone.Count < FeedPheromone.Threshold){//フェロモン探索状態のときに餌フェロモンの数が一定値をした下回ったとき
                State = AntState.Random;//ランダム探索状態に移行
            }

            // 進行方向の決定
            var pos = transform.position;
            if(State == AntState.BackHome) { DetectFeed = false; }
            if(State != AntState.BackHome) { DetectHome = false; }

            if(DetectFeed) { // 餌の方向を向く
                transform.LookAt(pos + FeedDirection);
                DetectFeed = false;
            }
            else if(DetectHome) { // 巣の方向を向く
                transform.LookAt(pos + HomeDirection);
            }
            else if(State == AntState.Random) { // ランダム探索状態
                transform.Rotate(new Vector3(0, (Random.value * 2 - 1) * 60, 0));
            }
            else if(State == AntState.PheromoneSearch) { // フェロモン探索状態
                transform.LookAt(pos + FeedPheromone.Direction);
                // 分散1，平均0の正規分布に従う乱数
                Z = Mathf.Sqrt(-2.0f * Mathf.Log(Random.value)) * Mathf.Cos(2.0f * Mathf.PI * Random.value); 
                transform.Rotate(new Vector3(0, 20f * Z * (1.0f - Sensitivity), 0));
            }
            else if(State == AntState.BackHome) { // 帰巣状態
                if(ColonyPheromone.Count >= ColonyPheromone.Threshold){//フェロモンの数が一定値を上回ったら、帰巣フェロモンの方向を向く
                    transform.LookAt(pos + ColonyPheromone.Direction);
                    Z = Mathf.Sqrt(-2.0f * Mathf.Log(Random.value)) * Mathf.Cos(2.0f * Mathf.PI * Random.value);
                    transform.Rotate(new Vector3(0, 20f * Z * (1.0f - Sensitivity), 0));
                }else{
                    transform.Rotate(new Vector3(0, (Random.value * 2 - 1) * 60, 0));
                }
            }

            Agent.enabled = true;

            // 目的地の設定
            pos += transform.forward * Speed * 0.1f;
            Agent.SetDestination(pos);

            // フェロモンの放出
            CurrentPheromoneStep += 1;
            if(CurrentPheromoneStep > PheromoneStep && Limitation.flg) {
                CurrentPheromoneStep = 0;
                if(State == AntState.Random || State == AntState.PheromoneSearch) {//ランダム探索状態またはフェロモン探索状態の時
                    GeneratePheromone(PheromonePrefab1, E * ColonyPheromone.R, ColonyPheromone.Alpha);//帰巣フェロモンを放出する
                }
                else if(State == AntState.BackHome) {//帰巣状態の時
                    GeneratePheromone(PheromonePrefab2, E * FeedPheromone.R, FeedPheromone.Alpha);//餌フェロモンを放出する
                }
            }

            // 内部活性の減衰
            E *= Alpha;

            // 探索の終了判定(下回ったありを活動停止させる)
            if(E < Threshold) {
                Debug.Log("death");
                ResetAnt();
            }

            CurrentTime = 0.0f;
        }

        debugText = $"{State.ToString()}\n"
                    + $"x = {transform.position.x}, z = {transform.position.z}\n"
                    + $"E = {E}\n"
                    + $"p1 cnt = {ColonyPheromone.Count}\n"
                    + $"p2 cnt = {FeedPheromone.Count}\n"
                    + $"next pos = {Agent.nextPosition}";

        ColonyPheromone.Reset();
        FeedPheromone.Reset();
    }

    public void ResetAnt() {
        Destroy(gameObject, 0.0f);
    }
    // setting a destination
    public void FindFeed(float amount) {
        State = AntState.BackHome;
        Agent.ResetPath();
        // 次に進行方向を決定するまでNavMeshAgentを停止させる
        Agent.enabled = false;
        transform.Rotate(new Vector3(0, 180, 0));
        AntRenderer.color = Color.red;
        // 内部活性の回復
        E = Mathf.Clamp(amount, 0, 1);
        Debug.Log("Find Feed");
    }

    private void GeneratePheromone(PheromoneController prefab, float pheromone, float alpha) {
        var controller = Instantiate(prefab, transform.position + new Vector3((Random.value - 0.5f) * 2.0f, 0.0f, (Random.value - 0.5f) * 2.0f), Quaternion.identity);
        controller.Pheromone = pheromone;
        controller.Alpha = alpha;
    }

    void OnTriggerStay(Collider collider) {
        // フェロモン、餌、巣の検出
        if(collider.gameObject.layer == ColonyPheromone.Layer) {
            var v = (collider.gameObject.transform.position - transform.position);
            // 内積からフェロモンの方向を計算する
            if(v.magnitude >= 0.01f && Vector3.Dot(v.normalized, transform.forward) > 0.5) {
                // フェロモンの強さ、距離に応じてベクトルを加算
                ColonyPheromone.Direction += collider.gameObject.GetComponent<PheromoneController>().Pheromone * v / Mathf.Pow(v.magnitude + 0.1f, 1.2f);
                ColonyPheromone.Count += 1;
            }
        }
        else if(collider.gameObject.layer == FeedPheromone.Layer) {
            var v = (collider.gameObject.transform.position - transform.position);
            if(v.magnitude >= 0.01f && Vector3.Dot(v.normalized, transform.forward) > 0.5) {
                FeedPheromone.Direction += collider.gameObject.GetComponent<PheromoneController>().Pheromone * v / Mathf.Pow(v.magnitude + 0.1f, 1.2f);
                FeedPheromone.Count += 1;
            }
        }
        // 餌と近いかどうか
        else if(collider.gameObject.layer == FeedLayer && State != AntState.BackHome) {
            DetectFeed = true;
            FeedDirection = (collider.gameObject.transform.position - transform.position).normalized;
        }
        // 巣と近いかどうか
        else if(collider.gameObject.layer == ColonyLayer && State == AntState.BackHome) {
            DetectHome = true;
            HomeDirection = (collider.gameObject.transform.position - transform.position).normalized;
        }   
    }
}
