use crate::action_set::{
  all_deck_ctrl::AllDeckControls,
  model::{ButtonState, ControllerAction, Movement},
};
use std::{
  sync::{mpsc, Arc, Mutex},
  thread,
  time::Duration,
};
use steamworks::{Client, ClientManager, Input, SIResult, SingleClient};
use steamworks_sys::InputHandle_t;

/// Run a function until it returns a value.
/// If the function returns `None`, wait for the specified interval and run the Steam callbacks.
fn poll<R, F>(single: &SingleClient, interval_ms: u64, mut f: F) -> R
where
  F: FnMut() -> Option<R>,
{
  loop {
    // call the function immediately, in case it can return a value without waiting
    match f() {
      Some(r) => return r,
      None => {}
    }

    thread::sleep(Duration::from_millis(interval_ms));
    single.run_callbacks();
  }
}

/// Poll to get connected controller handles.
fn poll_input_handles(
  single: &SingleClient,
  input: &Input<ClientManager>,
  interval_ms: u64,
) -> Vec<InputHandle_t> {
  poll(&single, interval_ms, || {
    let handles = input.get_connected_controllers();
    if !handles.is_empty() {
      println!("num of input handles: {:?}", handles.len());
      return Some(handles);
    }
    println!("no input handles, retrying...");
    return None;
  })
}

pub fn spawn(
  app_id: u32,
  interval_ms: u64,
  update_lock: Arc<Mutex<bool>>,
  ui_tx: mpsc::Sender<String>,
  network_tx: mpsc::Sender<ControllerAction>,
) -> SIResult<()> {
  let (client, single) = Client::init_app(app_id)?;

  thread::spawn(move || {
    let input = client.input();
    input.init(false);

    let mut all_deck_ctrl = poll(&single, 100, || match AllDeckControls::new(&input) {
      Ok(c) => Some(c),
      Err(_) => None,
    });

    let input_handles = poll_input_handles(&single, &input, 100);

    input.activate_action_set_handle(input_handles[0], all_deck_ctrl.handle);

    poll(&single, interval_ms, || {
      all_deck_ctrl.update(&input, input_handles[0]);

      let mut update = update_lock.lock().unwrap();
      if *update {
        // UI requested update
        ui_tx
          .send(
            all_deck_ctrl
              .repo
              .actions
              .iter()
              .map(|a| a.borrow().to_string())
              .collect::<Vec<String>>()
              .join("\n"),
          )
          .unwrap();

        // Network send new informations
        {
          let move_input = all_deck_ctrl.move1.borrow();
          let move_input = move_input.data;

          if let Some(data) = move_input {
            let movement = ControllerAction::Move(Movement {
              x: data.x,
              y: data.y,
            });
            network_tx.send(movement).unwrap();
          }
        }

        {
          let y_button = all_deck_ctrl.btn_y.borrow();
          let y_button = y_button.data;

          if let Some(data) = y_button {
            let pressed = ControllerAction::Button(ButtonState {
              y_button: data.bState,
            });

            network_tx.send(pressed).unwrap();
          }
        }
        *update = false;
      }

      None as Option<()> // run forever
    });
  });

  Ok(())
}
