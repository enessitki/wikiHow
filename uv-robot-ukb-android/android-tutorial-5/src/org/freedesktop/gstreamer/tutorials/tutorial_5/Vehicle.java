package org.freedesktop.gstreamer.tutorials.tutorial_5;

public class Vehicle {
//
//    Vehicle() {
//
//    }

    private String vehicleName = "";
    private String vehicleType = "";
    private boolean isConnected = false;
    private boolean isStreaming = false;
    private int wifiChannel = 0;
    private boolean isPositionUp = true;
    private int disconnected_policy = 0;
    private int wifi_channel = -1;
    private int returnHomeState = 0;
    private int payloadId = 0;
    private int batteryInfo = 0;
    private int direction = 0;
    private int armPosition = 0;
    private int frontLed = 0;
    private int backLed = 0;
    private int imuCommand = 0;
    private int driveMode = 0;
    private int cameraId = 0;
    private float latitude = 0;
    private float longitude = 0;

    private int IMU_RESET_READY_FLAG = 0;
    private int IMU_RESET_DETECT_FLAG = 0;
    private int IMU_SAVE_ANGLE_READY_FLAG = 0;
    private int IMU_SAVE_ANGLE_DETECT_FLAG = 0;
    private int IMU_SAVED_ANGLE_RESET_READY_FLAG = 0;
    private int IMU_SAVED_ANGLE_RESET_DETECT_FLAG = 0;
    private int TURN_SAVED_ANGLE_READY_FLAG = 0;
    private int TURN_SAVED_ANGEL_DETECT_FLAG = 0;

    private int IMU_RESET_COMMAND=0;
    private int IMU_SAVE_ANGLE_COMMAND=0;
    private int IMU_SAVED_ANGLE_RESET_COMMAND=0;
    private int TURN_SAVED_ANGLE_COMMAND=0;

    private int JUMP_READY_FLAG = 0;
    private int JUMP_DETECT_FLAG = 0;
    private int FIRE_READY_FLAG = 0;
    private int FIRE_DETECT_FLAG = 0;
    private int FUSE_READY_FLAG = 0;
    private int FUSE_DETECT_FLAG = 0;

    private int JUMP_COMMAND = 0;
    private int FIRE_COMMAND = 0;
    private int FUSE_COMMAND = 0;

    private int bit0 = 0b00000001;
    private int bit1 = 0b00000010;
    private int bit2 = 0b00000100;
    private int bit3 = 0b00001000;
    private int bit4 = 0b00010000;
    private int bit5 = 0b00100000;
    private int bit6 = 0b01000000;
    private int bit7 = 0b10000000;

    public String getVehicleName() {
        return vehicleName;
    }

    void setVehicleName(String vehicleName) {
        this.vehicleName = vehicleName;
    }

    public String getVehicleType() {
        return vehicleType;
    }

    void setVehicleType(String vehicleType) {
        if (vehicleType.contains("geko-"))
            this.vehicleType = "ika-1";
        else if(vehicleType.contains("komodo-"))
            this.vehicleType = "ika-2";
        else {
            this.vehicleType = "none";
        }
    }

    public boolean isConnected() {
        return isConnected;
    }

    public void setConnected(boolean connected) {
        isConnected = connected;
    }

    public boolean isStreaming() {
        return isStreaming;
    }

    public void setStreaming(boolean streaming) {
        isStreaming = streaming;
    }

    public boolean isPositionUp() {
        return isPositionUp;
    }

    public void setPositionUp(boolean positionUp) {
        isPositionUp = positionUp;
    }

    public int getDisconnected_policy() {
        return disconnected_policy;
    }

    public void setDisconnected_policy(int disconnected_policy) {
        this.disconnected_policy = disconnected_policy;
    }

    public int getWifiChannel() {
        return wifi_channel;
    }

    public void setWifiChannel(int wifi_channel) {
        this.wifi_channel = wifi_channel;
    }

    public int getReturnHomeState() {
        return returnHomeState;
    }

    public void setReturnHomeState(int returnHomeState) {
        this.returnHomeState = returnHomeState;
    }

    public int getPayloadId() {
        return payloadId;
    }

    public void setPayloadId(int payloadId) {
        this.payloadId = payloadId;
    }

    public int getBatteryInfo() {
        return batteryInfo;
    }

    public void setBatteryInfo(int batteryInfo) {
        this.batteryInfo = batteryInfo;
    }

    public int getDirection() {
        return direction;
    }

    public void setDirection(int direction) {
        this.direction = direction;
    }

    public int getArmPosition() {
        return armPosition;
    }

    public void setArmPosition(int armPosition) {
        this.armPosition = armPosition;
    }

    public int getFrontLed() {
        return frontLed;
    }

    public void setFrontLed(int frontLed) {
        this.frontLed = frontLed;
    }

    public int getBackLed() {
        return backLed;
    }

    public void setBackLed(int backLed) {
        this.backLed = backLed;
    }

    public int getImuCommand() {
        return imuCommand;
    }

    public void setImuCommand(int imuCommand) {
        this.imuCommand = imuCommand;
    }

    public int getDriveMode() {
        return driveMode;
    }

    public void setDriveMode(int driveMode) {
        this.driveMode = driveMode;
    }

    public int getCameraId() {
        return cameraId;
    }

    public void setCameraId(int cameraId) {
        this.cameraId = cameraId;
    }

    void updateImuStatus(int msg){
        IMU_RESET_READY_FLAG = msg & bit0;
        IMU_RESET_DETECT_FLAG = (msg & bit1) >> 1;
        IMU_SAVE_ANGLE_READY_FLAG = (msg& bit2) >> 2;
        IMU_SAVE_ANGLE_DETECT_FLAG = (msg & bit3) >> 3;
        IMU_SAVED_ANGLE_RESET_READY_FLAG = (msg & bit4) >> 4;
        IMU_SAVED_ANGLE_RESET_DETECT_FLAG = (msg & bit5) >> 5;
        TURN_SAVED_ANGLE_READY_FLAG = (msg & bit6) >> 6;
        TURN_SAVED_ANGEL_DETECT_FLAG = (msg& bit7) >> 7;

        IMU_RESET_COMMAND = commandStatus(IMU_RESET_COMMAND,
                IMU_RESET_READY_FLAG,
                IMU_RESET_DETECT_FLAG);

        IMU_SAVE_ANGLE_COMMAND = commandStatus(IMU_SAVE_ANGLE_COMMAND,
                IMU_SAVE_ANGLE_READY_FLAG,
                IMU_SAVE_ANGLE_DETECT_FLAG);

        IMU_SAVED_ANGLE_RESET_COMMAND = commandStatus(IMU_SAVED_ANGLE_RESET_COMMAND,
                IMU_SAVED_ANGLE_RESET_READY_FLAG,
                IMU_SAVED_ANGLE_RESET_DETECT_FLAG);

        TURN_SAVED_ANGLE_COMMAND = commandStatus(TURN_SAVED_ANGLE_COMMAND,
                TURN_SAVED_ANGLE_READY_FLAG,
                TURN_SAVED_ANGEL_DETECT_FLAG);

    }

    void updatePayloadStatus(int msg){
        JUMP_READY_FLAG = msg & bit0;
        JUMP_DETECT_FLAG = (msg & bit1) >> 1;
        FIRE_READY_FLAG = (msg & bit2) >> 2;
        FIRE_DETECT_FLAG = (msg & bit3) >> 3;
        FUSE_READY_FLAG = (msg & bit4) >> 4;
        FUSE_DETECT_FLAG = (msg & bit5) >> 5;

        JUMP_COMMAND = commandStatus(JUMP_COMMAND, JUMP_READY_FLAG, JUMP_DETECT_FLAG);
        FIRE_COMMAND = commandStatus(FIRE_COMMAND, FIRE_READY_FLAG, FIRE_DETECT_FLAG);
        FUSE_COMMAND = commandStatus(FUSE_COMMAND, FUSE_READY_FLAG, FUSE_DETECT_FLAG);
    }

    private int commandStatus(int command, int ready, int detect){
        if(detect==1)
            return 0;
        else
            return command;
    }

    public float getLatitude() {
        return latitude;
    }

    void setLatitude(float latitude) {
        this.latitude = latitude;
    }

    public float getLongitude() {
        return longitude;
    }

    void setLongitude(float longitude) {
        this.longitude = longitude;
    }

    int getImuState(int demand){
        if (demand == 0)
            return 0;

        else if( demand == 1)
            IMU_RESET_COMMAND = commandDecision(1, IMU_RESET_READY_FLAG, IMU_RESET_DETECT_FLAG);

        else if( demand == 2)
            IMU_SAVE_ANGLE_COMMAND = commandDecision(1, IMU_SAVE_ANGLE_READY_FLAG, IMU_SAVE_ANGLE_DETECT_FLAG);

        else if( demand == 4)
            IMU_SAVED_ANGLE_RESET_COMMAND = commandDecision(1, IMU_SAVED_ANGLE_RESET_READY_FLAG, IMU_SAVED_ANGLE_RESET_DETECT_FLAG);

        else if( demand == 8)
            TURN_SAVED_ANGLE_COMMAND = commandDecision(1, TURN_SAVED_ANGLE_READY_FLAG, TURN_SAVED_ANGEL_DETECT_FLAG);

        if (IMU_RESET_COMMAND == 1)
            return 1;

        else if( IMU_SAVE_ANGLE_COMMAND == 1)
            return 2;

        else if( IMU_SAVED_ANGLE_RESET_COMMAND == 1)
            return 4;

        else if( TURN_SAVED_ANGLE_COMMAND == 1)
            return 8;

        return 0;
    }

    int getPayloadState() {
        int demand = payloadId;
        if (demand == 0)
            return 0;

        else if( demand ==1)
            JUMP_COMMAND = commandDecision(1, JUMP_READY_FLAG, JUMP_DETECT_FLAG);

        else if( demand ==2)
            FIRE_COMMAND = commandDecision(1, FIRE_READY_FLAG, FIRE_DETECT_FLAG);

        else if( demand ==3)
            FUSE_COMMAND = commandDecision(1, FUSE_READY_FLAG, FUSE_DETECT_FLAG);

        if (JUMP_COMMAND == 1)
            return 1;

        else if( FIRE_COMMAND == 1)
            return 2;

        else if( FUSE_COMMAND == 1)
            return 4;

        return 0;
    }

    private int commandDecision(int command, int ready,int detect){
        if (ready == 1)
            return 1;
        else
            return 0;
    }


}
