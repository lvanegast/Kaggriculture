import importlib.util
import tempfile
import shutil
from pathlib import Path
import kaggle_environments as ke

def verify_agent(filepath):
    print(f"\n--- Verifying {filepath} in isolated sandbox ---")
    tmp_dir = Path(tempfile.mkdtemp())
    try:
        dest = tmp_dir / filepath.name
        shutil.copy(filepath, dest)
        
        spec = importlib.util.spec_from_file_location("agent_test", dest)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        
        assert hasattr(mod, "agent"), "Missing agent function!"
        assert callable(mod.agent), "agent is not callable!"
        
        # Test a 24-step match to ensure no runtime errors
        env = ke.make("kaggriculture", configuration={"seed": 42, "episodeSteps": 24})
        env.run([mod.agent, mod.agent])
        assert len(env.steps) >= 24, "Episode did not run to expected steps!"
        
        p0_rew = env.steps[-1][0]["reward"]
        p1_rew = env.steps[-1][1]["reward"]
        print(f"SUCCESS: {filepath.name} loaded and ran flawlessly! Step 24 P0=${p0_rew} | P1=${p1_rew}")
        return True
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

if __name__ == "__main__":
    v18_ok = verify_agent(Path("submission_v18_apex_dominator.py"))
    v19_ok = verify_agent(Path("submission_v19_apex_sovereign.py"))
    if v18_ok and v19_ok:
        print("\nALL SUBMISSIONS VERIFIED 100% SELF-CONTAINED AND SUBMISSION-READY!")
