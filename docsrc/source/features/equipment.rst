Equipment
#########

.. versionadded:: 0.8.0
.. versionchanged:: 0.9.1 added equipment visibility
.. versionchanged:: 0.9.3 added Kayaking and Canoeing to Boat
.. versionchanged:: 0.9.7 sports updated for Bike
.. versionchanged:: 0.9.10 added Board
.. versionchanged:: 0.10.3 added Standup paddleboarding to Board
.. versionchanged:: 0.11.0 added Tennis (Outdoor) to Shoes
.. versionchanged:: 1.0.0 added Padel (Outdoor) to Shoes
.. versionchanged:: 1.1.0 added Canoeing (Whitewater) and Kayaking (Whitewater) to Boat

Users can create equipment that can be associated with workouts.

.. figure:: ../_images/equipments-list.png
   :alt: FitTrackee Equipment


The following equipment types are available, depending on the sport:

- Bike: Cycling (Sport, Transport, Trekking), Halfbike, Mountain Biking and Mountain Biking (Electric),
- Bike Trainer: Cycling (Virtual),
- Board: Standup paddleboarding and Windsurfing,
- Kayak/Boat: Canoeing, Canoeing (Whitewater), Rowing, Kayaking and Kayaking (Whitewater),
- Shoes: Hiking, Mountaineering, Padel (Outdoor), Running, Tennis (Outdoor), Trail and Walking,
- Skis: Skiing (Alpine and Cross Country),
- Snowshoes: Snowshoes.

Users can define equipment visibility:

- private: only owner can see the equipment in workout detail,
- followers only: only owner and followers can see the equipment in workout detail,
- public: anyone can see the equipment in workout detail even unauthenticated users.

.. figure:: ../_images/equipment-detail.png
   :alt: FitTrackee Equipment Detail

The equipment details are only visible to its owner.

For now only, only one piece of equipment can be associated with a workout.

Following totals are displayed for each piece of equipment:

- total distance
- total duration
- total workouts

.. note::
  | In case of an incorrect total (although this should not happen), it is possible to recalculate totals.

It is possible to define default equipment for sports: when adding a workout, the equipment will automatically be displayed in the dropdown list depending on selected sport.

An equipment can be edited (label, equipment type, description, visibility, active status and default sports).

.. warning::
  | Changing equipment type will remove all existing workouts associations for that piece of equipment and default sports.

Deactivated equipment will not appear in dropdown when **a workout is added**. It remains displayed in the details of the workout, to which it was associated before being deactivated.

.. note::
  | An equipment type can be deactivated by an administrator.
