// Copyright (c) FIRST and other WPILib contributors.
// Open Source Software; you can modify and/or share it under the terms of
// the WPILib BSD license file in the root directory of this project.
package frc.robot.subsystems;

import edu.wpi.first.networktables.NetworkTable;
import edu.wpi.first.networktables.NetworkTableEntry;
import edu.wpi.first.networktables.NetworkTableInstance;
import edu.wpi.first.wpilibj.smartdashboard.SmartDashboard;
import edu.wpi.first.wpilibj2.command.SubsystemBase;

public class ExampleSubsystem extends SubsystemBase {
  private NetworkTableInstance tableInstance = NetworkTableInstance.getDefault();
  private NetworkTable table;
  private NetworkTableEntry rx, ry, ra, rc;
  private double x, y, area, numberOfTargets;
  private String name;
  private int networkTableReadCounter = 0;

  /** Creates a new ExampleSubsystem. */
  public ExampleSubsystem(String name) {
    this.name = name;
    table = tableInstance.getTable(name);

    rx = table.getEntry("cx");
    ry = table.getEntry("cy");
    ra = table.getEntry("ca");
    rt = table.getEntry("ct");
  }

  /**
   * @return true when examplesubsystem sees a target, false when not seeing a target
   */
  public boolean seesTarget() {
    return (numberOfTargets>0);
  }

  /**
   * @return true when ExampleSubsystem is connected & reading data
   * false when ExampleSubsystem is disconnected or not reading any data
   */
  public boolean isGettingData() {
    return (x != 1000 && y != 1000 && area != 1000 && numberOfTargets != 1000);
  }

  public void readData() {
    double _x, _y, _numberOfTargets, _area; 
    _numberOfTargets = rt.getDouble(1000.0);
    _area = ra.getDouble(1000.0);
    _x = rx.getDouble(1000.0);
    _y = ry.getDouble(1000.0);
    networkTableReadCounter = 0;
  
    // Check if the pivision updated the NetworkTable while we were reading values, to ensure that all
    // of the data (targetExists, X, Y, etc) are from the same vision frame.
    do {
      numberOfTargets = _numberOfTargets;
      area = _area;
      x = _x;
      y = _y;

      _numberOfTargets = rt.getDouble(1000.0);
      _area = ra.getDouble(1000.0);
      _x = rx.getDouble(1000.0);
      _y = ry.getDouble(1000.0);
      networkTableReadCounter++;
    } while(networkTableReadCounter<= 5 && (_x != x || _y != y || _area != area || _numberOfTargets != numberOfTargets));

  }

  @Override
  public void periodic() {
    readData();

    SmartDashboard.putNumber("Vision area", area);
    SmartDashboard.putNumber("Vision x", x);
    SmartDashboard.putNumber("Vision y", y);
    SmartDashboard.putNumber("Vision targets", numberOfTargets);
    SmartDashboard.putBoolean("Vision Updating", isGettingData());
    }
  }
}
