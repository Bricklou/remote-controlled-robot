use std::{sync::mpsc, thread, time::Duration};

use rumqttc::{Client, MqttOptions, QoS};

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

const TOPIC: &str = "robot";

pub fn spawn(interval_ms: u64, rx: mpsc::Receiver<ControllerAction>) {
  thread::spawn(move || {
    let mut previous_movement = Movement::default();
    let mut previous_y_btn = false;

    println!("Trying to connect to robot");

    let mut mqtt_options = MqttOptions::new("rumqtt-sync", "192.168.1.43", 1883);
    mqtt_options.set_credentials("mosquitto", "mosquitto");
    mqtt_options.set_keep_alive(Duration::from_secs(5));

    let (client, mut connection) = Client::new(mqtt_options, 10);

    thread::spawn(move || {
      // Iterate to poll the eventloop for connection progress
      for _ in connection.iter().enumerate() {}
    });

    poll(interval_ms, || {
      let action = rx.recv().unwrap();

      match action {
        ControllerAction::Move(movement) => {
          if movement != previous_movement {
            client
              .publish(
                TOPIC,
                QoS::AtLeastOnce,
                false,
                format!("move {:.3} {:.3}", movement.x, movement.y),
              )
              .expect("Failed to publish message");
            previous_movement = movement;
          }
        }
        ControllerAction::Button(state) => {
          if state.y_button && state.y_button != previous_y_btn {
            println!("button Y pressed");
            match client.publish(TOPIC, QoS::AtLeastOnce, false, "led") {
              Ok(_) => log::info!("Message published successfully"),
              Err(e) => {
                log::error!("Failed to publish message: {:?}", e)
              }
            }
          }
          previous_y_btn = state.y_button;
        }
      }

      None as Option<()> // run forever
    })
  });
}
