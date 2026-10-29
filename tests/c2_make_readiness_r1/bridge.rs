// Included only inside the production Bridge module in a disposable CI checkout.
// Typed outcome/artifact-availability inputs. No child, raw device, OS gesture,
// product code edit, private test expectation or shipping injection route.
use super::*;
use crate::{report::Reading,state::Making};
use serde_json::{json,Value};

#[test]
fn capture_contract_readiness() {
    let cases:Vec<Value>=serde_json::from_str(include_str!(env!("DT_C2_CASES"))).unwrap();
    let mut rows=Vec::new();
    for c in cases {
        let data=std::env::temp_dir().join(format!("verifier370-{}",children::nonce()));
        let(b,_rx)=Bridge::channel(data.clone(),Arc::new(|_|{}));
        {
            let mut core=b.core.lock().unwrap();
            core.app.folders=vec![PathBuf::from("Music")];
            let generation=core.app.begin_job("c2-readiness-fixture");
            let success=c["successful_current_check"].as_bool().unwrap();
            let o=Outcome{exit:Some(if success{0}else{2}),stderr:String::new(),
                reading:Reading::Unusable("typed outcome fixture"),total_frames:if success{Some(44100)}else{None},cancelled:false};
            assert!(core.app.finish_job(generation,"c2-readiness-fixture",&o));
            if c["label"].as_bool().unwrap(){assert!(core.app.set_label("C2 Music"));}
            if c["retained_audio"].as_bool().unwrap(){core.app.audio=Some(data.join("modeled-retained-audio.wav"));}
            let n=c["cards"].as_u64().unwrap();
            let ticket=core.app.begin_cards();
            let hint=discovery::Hint{sizes:(0..n).map(|_|64_000_000_000).collect(),
                paths:(0..n).map(|i|format!("MODEL-CARD-{i}")).collect(),unprobed:0};
            assert!(core.app.finish_cards(ticket,&Judged{hint:Some(hint),id_specific:None},String::new()));
            core.app.making=match c["mode"].as_str().unwrap(){
                "idle"=>Making::Idle,
                "confirm"=>Making::Confirm{dev:"MODEL-CARD-0".into(),bytes:64_000_000_000},
                "making"=>Making::Running{fraction:0.0,step:"safety"},
                _=>panic!("unknown independently issued mode"),
            };
        }
        let view=b.snapshot();
        rows.push(json!({"id":c["id"],"make_enabled":view.make_enabled}));
        assert!(b.trace.lock().unwrap().is_empty(),"snapshot fixture scheduled work");
    }
    std::fs::write(std::env::var("DT_C2_OUTPUT").unwrap(),serde_json::to_vec_pretty(&rows).unwrap()).unwrap();
}
