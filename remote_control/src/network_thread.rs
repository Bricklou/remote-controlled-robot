use std::{
  io::Write,
  net::TcpStream,
  sync::{mpsc, Mutex},
  thread,
  time::Duration,
};

use crate::action_set::model::{ControllerAction, Movement};

/// Run a function until it returns a value.
/// If the function returns `None`, wait for the specified interval and run the Steam callbacks.
fn poll<R, F>(interval_ms: u64, mut f: F) -> R
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
  }
}

pub fn spawn(interval_ms: u64, rx: mpsc::Receiver<ControllerAction>) {
  thread::spawn(move || {
    let mut previous_movement = Movement::default();
    let mut previous_y_btn = false;

    println!("Trying to connect to robot");
    let client_stream =
      TcpStream::connect("192.168.31.128:4835").expect("Failed to connect to remote robot");
    let client_stream = Mutex::new(client_stream);

    poll(interval_ms, || {
      let action = rx.recv().unwrap();

      match action {
        ControllerAction::Move(movement) => {
          if movement != previous_movement {
            let mut stream = client_stream.lock().unwrap();
            stream
              .write_fmt(format_args!("move {:.3} {:.3}\n", movement.x, movement.y))
              .unwrap();
            previous_movement = movement;
          }
        }
        ControllerAction::Button(state) => {
          if state.y_button && state.y_button != previous_y_btn {
            let mut stream = client_stream.lock().unwrap();
            println!("button Y pressed");
            stream.write_fmt(format_args!("led\n")).unwrap();
          }
          previous_y_btn = state.y_button;
        }
      }

      None as Option<()> // run forever
    });
  });
}
