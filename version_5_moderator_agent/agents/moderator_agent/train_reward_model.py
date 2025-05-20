from agents.moderator_agent.agent import ModeratorAgent
from trl import PPOTrainer, PPOConfig
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from datasets import Dataset
import requests
import pandas as pd

def train_reward_model(data):
    # reward model 학습 로직 구현
    pass

def train_rlhf_policy(rlhf_df):
    # rlhf_df: DataFrame with columns ["prompt", "response", "reward"]
    # 1. 데이터셋 변환
    dataset = Dataset.from_pandas(rlhf_df)
    # 2. 모델/토크나이저 준비
    model_name = "gpt2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    # 3. PPOTrainer 설정
    config = PPOConfig(
        model_name=model_name,
        learning_rate=1.41e-5,
        batch_size=2,
        mini_batch_size=1,
        log_with=None,
    )
    ppo_trainer = PPOTrainer(
        config=config,
        model=model,
        tokenizer=tokenizer,
        dataset=dataset,
        reward_fn=lambda samples, **kwargs: [x["reward"] for x in samples]
    )
    # 4. 학습 루프 (간단 예시)
    for epoch in range(3):
        for sample in dataset:
            query = sample["prompt"]
            response = sample["response"]
            reward = sample["reward"]
            ppo_trainer.step([query], [response], [reward])
    # 5. 학습된 모델 저장
    model.save_pretrained("./ppo_rlhf_model")
    tokenizer.save_pretrained("./ppo_rlhf_model")

def fetch_feedback_log():
    # Moderator Agent 서버에서 피드백 로그를 가져옴
    resp = requests.get("http://localhost:10010/export_feedback_log")
    return resp.json()

def make_rlhf_dataset(feedback_log):
    data = []
    for entry in feedback_log:
        prompt = f"State: {entry['utg']}, Feedback: {entry['feedback']}, Negotiation: {entry.get('negotiation')}"
        response = entry.get("response", "...")  # Autonomous Agent의 행동/응답
        reward = entry["reward"]
        data.append({"prompt": prompt, "response": response, "reward": reward})
    return pd.DataFrame(data)

def main():
    # 1. 피드백 로그 수집
    feedback_log = fetch_feedback_log()
    # 2. RLHF 학습 데이터셋 변환
    rlhf_df = make_rlhf_dataset(feedback_log)
    # 3. RLHF(PPO) 학습
    train_rlhf_policy(rlhf_df)
    # 4. (서비스 코드에서) 학습된 모델로 정책 업데이트

if __name__ == "__main__":
    main()

# ModeratorAgent 인스턴스가 이미 생성되어 있다고 가정
reward_data = moderator_agent.export_for_reward_model()
train_reward_model(reward_data)
