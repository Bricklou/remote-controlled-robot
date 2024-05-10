mod action_set;
mod input_thread;
mod network_thread;
mod ui_thread;
mod utils;

use std::sync::{mpsc, Arc, Mutex};

use action_set::model::ControllerAction;

fn main() -> iced::Result {
  env_logger::init(); // log to stderr (if you run with `RUST_LOG=debug`)

  let update_lock = Arc::new(Mutex::new(false));
  let (ui_tx, ui_rx) = mpsc::channel::<String>();
  let (network_tx, network_rx) = mpsc::channel::<ControllerAction>();

  input_thread::spawn(
    480, // app id
    1,   // interval of polling input events
    update_lock.clone(),
    ui_tx,
    network_tx,
  )
  .unwrap();

  network_thread::spawn(1, network_rx);

  ui_thread::run(
    30, // interval of updating UI
    update_lock,
    ui_rx,
  )
}
