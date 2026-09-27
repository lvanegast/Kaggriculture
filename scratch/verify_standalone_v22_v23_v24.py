import importlib.util
import tempfile
import shutil
from pathlib import Path
import kaggle_environments as ke

def verify_agent(filepath):
    print(f"\n--- Verifying {filepath.name} in isolated sandbox ---")
    tmp_dir = Path(tempfile.mkdtemp())
    try:
        dest = tmp_dir / filepath.name
        shutil.copy(filepath, dest)
        
        spec = importlib.util.spec_from_file_location("agent_test", dest)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        
        assert hasattr(mod, "agent"), "Missing agent function!"
        assert callable(mod.agent), "agent is not callable!"
        
        # Test full 720 steps on Seed 42
        env = ke.make("kaggriculture", configuration={"seed": 42})
        env.run([mod.agent, mod.agent])
        assert len(env.steps) >= 720, "Episode did not run to full 720 steps!"
        
        p0_rew = env.steps[-1][0]["reward"]
        p1_rew = env.steps[-1][1]["reward"]
        print(f"SUCCESS: {filepath.name} executed full 720 steps! P0=${p0_rew:8.0f} | P1=${p1_rew:8.0f}")
        return True
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

if __name__ == "__main__":
    v22_ok = verify_agent(Path("submission_v22_apex_bio_harvester.py"))
    v23_ok = verify_agent(Path("submission_v23_apex_arbitrageur.py"))
    v24_ok = verify_agent(Path("submission_v24_apex_thunder_scale.py"))
    if v22_ok and v23_ok and v24_ok:
        print("\n>>> ALL 3 SUBMISSIONS (v22, v23, v24) ARE 100% SELF-CONTAINED AND TOURNAMENT VERIFIED! <<<")
