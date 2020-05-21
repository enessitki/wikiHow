package org.freedesktop.gstreamer.tutorials.tutorial_5;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.Dialog;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.media.MediaRecorder;
import android.net.ConnectivityManager;
import android.net.wifi.WifiInfo;
import android.net.wifi.WifiManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.provider.Settings;
import android.support.annotation.NonNull;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.util.Log;
import android.view.MotionEvent;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.Window;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.SeekBar;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.ToggleButton;

import org.freedesktop.gstreamer.GStreamer;

//import android.databinding.BaseObservable;
//import android.databinding.Bindable;
//import android.text.TextUtils;
//import android.util.Patterns;
//
//import com.android.databinding.library.baseAdapters.BR;

import java.io.File;
import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.util.Arrays;
import java.util.Date;
import java.util.Timer;
import java.util.TimerTask;

import io.github.controlwear.virtual.joystick.android.JoystickView;

import static android.content.ContentValues.TAG;


public class Tutorial5 extends Activity implements SurfaceHolder.Callback {
    final Context context = this;
    private native void nativeInit();     // Initialize native code, build pipeline, etc
    private native void nativeFinalize(); // Destroy pipeline and shutdown native code
    private native void nativePlay();     // Set pipeline to PLAYING
    private native void nativePause();    // Set pipeline to PAUSED
    private static native boolean nativeClassInit(); // Initialize native class: cache Method IDs for callbacks
    private native void nativeSurfaceInit(Object surface);
    private native void nativeSurfaceFinalize();
    private native void nativeVideoFlip();
    private native void nativeVideoFlipTo0();
    private native void nativeVideoFlipTo2();
    private native void nativeScreenShot(String myFile);
    private native void nativeStartRecord(String myFile);
    private long native_custom_data;      // Native code will use this to keep private data

    private boolean is_playing_desired;   // Whether the user asked to go to PLAYING
    private boolean isAutoFlipOn = false;
    private Timer motionDetectionTimer ;
    private TimerTask motionDetectionTimerTask;
    final Handler motionDetectionTimerHandler = new Handler();
    private int motionDetectorState = 0;
    private float motionThreshold = 10000;
    private long motionDuration = 10000;
    private long motionStartTime = 0;

    // udp
    private Timer udpTimer ;
    private TimerTask udpTimerTask;
    final Handler udpTimerHandler = new Handler();
    private DatagramSocket receiveSocket;
    private byte[] receiveData = new byte[21];

    private DatagramSocket sendSocket;
    private InetAddress vehicleIp;



    // dialogs
    private Dialog infoDialog;
    private TextView infoDialogText;
    private Dialog configDialog;

    private ImageButton playButton;
    private ImageButton motionDetectionButton;
    private ImageView directionImage;
    private SeekBar batteryInfoImage;
    private TextView batteryInfoText;
    private ImageView armPositionImage;

    private JoystickView control1;
    private JoystickView control2;

    private Spinner driveSpeedSpinner;
    private int frontLedState = 0;
    private int backLedState = 0;
    private Spinner driveModeSpinner;
    private Spinner autoFixSpinner;
    private Spinner imuSpinner;
    private Spinner cameraSpinner;
    private boolean isPayloadActive = false;
    private boolean isReturnHome = false;
    private boolean isDestructOn = false;
    private boolean isRefreshWifi = false;
    private Spinner wifiChannelSpinner;
    private boolean battery_warning_10 = true;
    private boolean battery_warning_20 = true;
    private boolean battery_warning_30 = true;
    private Spinner disconnectionPolicySpinner;
    private boolean isRecording = false;

    private MediaRecorder mediaRecorder;

    private Vehicle vehicle = new Vehicle();

    // Called when the activity is first created.
    @SuppressLint("ClickableViewAccessibility")
    @Override
    public void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);

        // permissions
        if(ContextCompat.checkSelfPermission(
                this, Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED){

//            ActivityCompat.shouldShowRequestPermissionRationale(this,
//                    Manifest.permission.WRITE_EXTERNAL_STORAGE);

            requestPermissions(new String[] {Manifest.permission.WRITE_EXTERNAL_STORAGE},10);
        }

        if(ContextCompat.checkSelfPermission(
                this, Manifest.permission.READ_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED){
            requestPermissions(new String[] {Manifest.permission.READ_EXTERNAL_STORAGE},11);
        }

        if(ContextCompat.checkSelfPermission(
                this, Manifest.permission.CAPTURE_AUDIO_OUTPUT) != PackageManager.PERMISSION_GRANTED){
            requestPermissions(new String[] {Manifest.permission.CAPTURE_AUDIO_OUTPUT},12);
        }

        if(ContextCompat.checkSelfPermission(
                this, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED){
            ActivityCompat.shouldShowRequestPermissionRationale(this,
            Manifest.permission.RECORD_AUDIO);
            requestPermissions(new String[] {Manifest.permission.RECORD_AUDIO},13);
        }

//        int YOUR_REQUEST_CODE = 200; // could be something else..
//        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) //check if permission request is necessary
//        {
//            ActivityCompat.requestPermissions(this,
//                    new String[] {android.Manifest.permission.RECORD_AUDIO, android.Manifest.permission.WRITE_EXTERNAL_STORAGE}, YOUR_REQUEST_CODE);
//        }

//        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
//
//            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.RECORD_AUDIO},
//                    Manifest.permission.RECORD_AUDIO);
//
//        }

        // Initialize GStreamer and warn if it fails
        try {
            GStreamer.init(this);
        } catch (Exception e) {
            Toast.makeText(this, e.getMessage(), Toast.LENGTH_LONG).show();
            finish();
            return;
        }

        // init udp
        try {
            receiveSocket = new DatagramSocket(5002);
            receiveSocket.setReceiveBufferSize(21);
            receiveSocket.setSoTimeout(50);

            sendSocket = new DatagramSocket(5001);
            sendSocket.setSoTimeout(50);
            vehicleIp = InetAddress.getByName("10.42.0.1");

//            udpReceive();
        } catch (SocketException | UnknownHostException e) {
            e.printStackTrace();
        }


        // set context view
        setContentView(R.layout.main);

        // set widget vars
        playButton = (ImageButton) findViewById(R.id.button_play);
        playButton.setEnabled(false);

        final SurfaceView sv = (SurfaceView) this.findViewById(R.id.surface_video);
        final SurfaceHolder sh = sv.getHolder();
        sh.addCallback(this);

        motionDetectionButton = (ImageButton) this.findViewById(R.id.button_motion_detect);

        infoDialog = new Dialog(context);
        infoDialog.requestWindowFeature(Window.FEATURE_NO_TITLE);
        infoDialog.setContentView(R.layout.info_dialog);
        infoDialogText = infoDialog.findViewById(R.id.text_info_dialog);

        Button infoDialogButton = (Button) infoDialog.findViewById(R.id.button_info_dialog_close);

        infoDialogButton.setOnClickListener(new OnClickListener() {
            @Override
            public void onClick(View view) {
                infoDialog.dismiss();
            }
        });

        configDialog = new Dialog(context);
        configDialog.requestWindowFeature(Window.FEATURE_NO_TITLE);
        configDialog.setContentView(R.layout.config_dialog);

        directionImage = findViewById(R.id.image_direction);

        findViewById(R.id.button_video_flip).setOnLongClickListener(new View.OnLongClickListener() {
            @Override
            public boolean onLongClick(View view) {
                isAutoFlipOn = !isAutoFlipOn;
                if(isAutoFlipOn)
                    view.setBackground(getDrawable(R.drawable.ic_rotate_90_degrees_ccw_white_24dp));
                else
                    view.setBackground(getDrawable(R.drawable.ic_rotate_left_white_24dp));
                return true;
            }
        });

        batteryInfoImage = (SeekBar) findViewById(R.id.image_ika_battery);
//        batteryInfoImage.setEnabled(false);
        batteryInfoImage.setOnTouchListener(new View.OnTouchListener(){
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                return true;
            }
        });
//        batteryInfoImage.setOnTouchListener(new View.OnTouchListener(){
//            @Override
//            public boolean onTouch(View v, MotionEvent event) {
//                return false;
//            }
//        });
        batteryInfoText = (TextView) findViewById(R.id.text_ika_battery_info);
        armPositionImage = (ImageView) findViewById(R.id.image_arm_position);

        control1 = (JoystickView) findViewById(R.id.control_1);
        control1.setAutoReCenterButton(true);
        control1.setFixedCenter(true);
        control2 = (JoystickView) findViewById(R.id.control_2);
        control2.setAutoReCenterButton(true);
        control2.setFixedCenter(true);

        driveSpeedSpinner = (Spinner) findViewById(R.id.spinner_drive_speed);

        driveModeSpinner = (Spinner) findViewById(R.id.spinner_drive_mode);
        autoFixSpinner = (Spinner) configDialog.findViewById(R.id.spinner_auto_fix);
        imuSpinner = (Spinner) findViewById(R.id.spinner_imu);
        cameraSpinner = (Spinner) findViewById(R.id.spinner_camera);
        wifiChannelSpinner = (Spinner) configDialog.findViewById(R.id.spinner_wifi_channel);
        disconnectionPolicySpinner = (Spinner) configDialog.findViewById(R.id.spinner_disconnection_policy);

        mediaRecorder = new MediaRecorder();
        mediaRecorder.setAudioSource(MediaRecorder.AudioSource.MIC);
        mediaRecorder.setOutputFormat(MediaRecorder.OutputFormat.THREE_GPP);
        mediaRecorder.setAudioEncoder(MediaRecorder.OutputFormat.AMR_NB);

        //--------------
        if (savedInstanceState != null) {
            is_playing_desired = savedInstanceState.getBoolean("playing");
            Log.i ("GStreamer", "Activity created. Saved state is playing:" + is_playing_desired);
        } else {
            is_playing_desired = false;
            Log.i ("GStreamer", "Activity created. There is no saved state, playing: false");
        }


        nativeInit();

        checkConnection();
    }

    @Override
    public void onRequestPermissionsResult(final int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        if (true){//(grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            if(requestCode == 13)
            {
                Log.i(TAG, "Permission granted");
                //do what you wanted to do
            }
            else if(requestCode == 12)
            {
                Log.i(TAG, "Permission granted 2");
                //do what you wanted to do
            }
        } else {
            Log.d(TAG, "Permission failed");
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        startUdpTimer();
    }

    protected void onSaveInstanceState (Bundle outState) {
        Log.d ("GStreamer", "Saving state, playing:" + is_playing_desired);
        outState.putBoolean("playing", is_playing_desired);
    }

    protected void onDestroy() {
        stopTimerTask();
        nativeFinalize();

        stopUdpTimerTask();

        super.onDestroy();
    }

    // Called from native code. This sets the content of the TextView from the UI thread.
    private void setMessage(final String message) {
        final TextView tv = (TextView) this.findViewById(R.id.textview_message);
        runOnUiThread (new Runnable() {
            public void run() {
                tv.setText(message);
            }
        });
    }

    // Called from native code. Native code calls this once it has created its pipeline and
    // the main loop is running, so it is ready to accept commands.
    private void onGStreamerInitialized () {
        Log.i ("GStreamer", "Gst initialized. Restoring state, playing:" + is_playing_desired);
        // Restore previous playing state
        if (is_playing_desired) {
            nativePlay();
        } else {
            nativePause();
        }

        // Re-enable buttons, now that GStreamer is initialized
        final Activity activity = this;
        runOnUiThread(new Runnable() {
            public void run() {
                activity.findViewById(R.id.button_play).setEnabled(true);
//                activity.findViewById(R.id.button_stop).setEnabled(true);
            }
        });
    }

    static {
        System.loadLibrary("gstreamer_android");
        System.loadLibrary("tutorial-5");
        nativeClassInit();
    }

    public void surfaceChanged(SurfaceHolder holder, int format, int width,
                               int height) {
        Log.d("GStreamer", "Surface changed to format " + format + " width "
                + width + " height " + height);

        nativeSurfaceInit (holder.getSurface());
    }

    public void surfaceCreated(SurfaceHolder holder) {
        Log.d("GStreamer", "Surface created: " + holder.getSurface());
    }

    public void surfaceDestroyed(SurfaceHolder holder) {
        Log.d("GStreamer", "Surface destroyed");
        nativeSurfaceFinalize ();
    }

    public void checkConnection(View view){
        checkConnection();
    }

    public void checkConnection(){
        ConnectivityManager manager = (ConnectivityManager)
                getSystemService(Tutorial5.CONNECTIVITY_SERVICE);

        Boolean isWifi = manager.getNetworkInfo(
                ConnectivityManager.TYPE_WIFI).isConnectedOrConnecting();

        if (! isWifi)
            startActivity(new Intent(Settings.ACTION_WIFI_SETTINGS));
        else {
            WifiManager wifiManager = (WifiManager) getApplicationContext().getSystemService (Context.WIFI_SERVICE);
            WifiInfo info = wifiManager.getConnectionInfo ();
            String ssid  = info.getSSID();

            int [] frequencyList = {0, 2412, 2417, 2422, 2427, 2432, 2437, 2442, 2447,
                    2452, 2457, 2462, 2467, 2472, 2484};

            int frequency = info.getFrequency();

            for (int i=0;i< frequencyList.length;i++){
                if(frequencyList[i]==frequency){
                    vehicle.setWifiChannel(i);
                    wifiChannelSpinner.setSelection(i);
                    break;
                }
            }

            if (!ssid.contains("geko-") && !ssid.contains("komodo-"))
                startActivity(new Intent(Settings.ACTION_WIFI_SETTINGS));
            else {
                vehicle.setVehicleName(ssid);
                vehicle.setVehicleType(ssid);
                vehicle.setConnected(true);
                playStream();
            }
        }

        Log.d("onClick:", isWifi.toString());
    }

    public void playStream(View view){
        playStream();

    }

    public  void  playStream(){
//        if (!is_playing_desired && vehicle.isConnected()){
        if (!is_playing_desired){
            is_playing_desired = true;
            nativePlay();
            playButton.setBackground(getDrawable(R.drawable.ic_pause_white_24dp));
        }
        else {
            is_playing_desired = false;
            nativePause();
            playButton.setBackground(getDrawable(R.drawable.ic_play_arrow_white_24dp));
        }

    }

    public void flipVideo(View view){
        if(!isAutoFlipOn)
            nativeVideoFlip();
    }

    public void screenShot(View view){
        screenShot();
        Toast toast = Toast.makeText(context, getString(R.string.screen_shot_taken), Toast.LENGTH_SHORT);
        toast.show();
    }

    public void screenShot(){
        Date now = new Date();
        android.text.format.DateFormat.format("yyyy-MM-dd_hh-mm-ss", now);
        String myFile=Environment.getExternalStorageDirectory() + File.separator +
                "Resimler"+ File.separator+
                "sc-"+now+".png";
//        Log.d("-----------------------",myFile);
        nativeScreenShot(myFile);
    }

    public void showConfigDialog(View view){
        if(!configDialog.isShowing())
            configDialog.show();
    }

    public void startRecoding(View view){
        isRecording = ! isRecording;

//        mediaRecorder.setAudioSource(MediaRecorder.AudioSource.VOICE_CALL);
//        mediaRecorder.setVideoSource(MediaRecorder.VideoSource.SURFACE);
//        mediaRecorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4); //THREE_GPP
//        mediaRecorder.setOutputFile(Environment.getExternalStorageDirectory() + File.separator + "Videolar" + File.separator + "video.mp4");
//        mediaRecorder.setVideoSize(1280, 720);
//        mediaRecorder.setVideoEncoder(MediaRecorder.VideoEncoder.H264);
//        mediaRecorder.setAudioEncoder(MediaRecorder.AudioEncoder.AMR_NB);
//        mediaRecorder.setVideoEncodingBitRate(512 * 1000);
//        mediaRecorder.setVideoFrameRate(15); // 30
//        mediaRecorder.setVideoEncodingBitRate(3000000);
//        int rotation = getWindowManager().getDefaultDisplay().getRotation();
//        int orientation = ORIENTATIONS.get(rotation + 90);
//        mediaRecorder.setOrientationHint(orientation);


        if (isRecording){
            Date now = new Date();
            android.text.format.DateFormat.format("yyyy-MM-dd_hh-mm-ss", now);
            String myFile=Environment.getExternalStorageDirectory() + File.separator +
                    "Videolar"+ File.separator+
                    "video-"+now+".3gp";
//
//            nativeStartRecord(myFile);
//
            view.setBackground(getDrawable(R.drawable.ic_stop_red_900_24dp));


            mediaRecorder.setOutputFile(myFile);
            try {
                mediaRecorder.prepare();
                mediaRecorder.start();
            } catch (IOException e) {
                e.printStackTrace();
            }


        }

        else {
            view.setBackground(getDrawable(R.drawable.ic_stop_white_24dp));
//            nativeStartRecord("");
            mediaRecorder.stop();
        }


    }

    public void setFrontLedState(View view){
        frontLedState += 1;
        if (frontLedState == 2)
            frontLedState = 3;

        if (frontLedState >3)
            frontLedState = 0;

        if (frontLedState == 0)
            view.setBackground(getDrawable(R.drawable.ic_brightness_1_black_24dp));

        else if (frontLedState == 1)
            view.setBackground(getDrawable(R.drawable.ic_brightness_3_white_24dp));

        else if (frontLedState == 3)
            view.setBackground(getDrawable(R.drawable.ic_brightness_2_white_24dp));
    }

    public void setBackLedState(View view){
        backLedState += 1;
        if (backLedState == 2)
            backLedState = 3;

        if (backLedState >3)
            backLedState = 0;

        if (backLedState == 0)
            view.setBackground(getDrawable(R.drawable.ic_brightness_1_black_24dp));

        else if (backLedState == 1)
            view.setBackground(getDrawable(R.drawable.ic_brightness_3_white_24dp));

        else if (backLedState == 3)
            view.setBackground(getDrawable(R.drawable.ic_brightness_2_white_24dp));
    }

    public void setPayloadActive(View view){
        ToggleButton toggle = configDialog.findViewById(R.id.toggle_payload);
        if(toggle.isChecked()){
            isPayloadActive = true;
            toggle.setChecked(false);

        }

    }

    public void setReturnHome(View view){
        ToggleButton toggle = configDialog.findViewById(R.id.toggle_return_home);
        if(toggle.isChecked()){
            isReturnHome = ! isReturnHome;
            toggle.setChecked(false);
        }
    }

    public void setDestructOn(View view){
        ToggleButton toggle = configDialog.findViewById(R.id.toggle_destruct_on);
        if(toggle.isChecked()){
            isDestructOn= ! isDestructOn;
            toggle.setChecked(false);
        }
    }

    public void setRefreshWifi(View view){
        isRefreshWifi = true;
    }



    public void startMotionDetection(View view){
        if(motionDetectionTimer == null){
            motionDetectorState = 0;
            startTimer();
            motionDetectionButton.setBackground(getDrawable(R.drawable.ic_directions_walk_red_900_24dp));
        }
        else {
            stopTimerTask();
            motionDetectorState = 0;
            motionDetectionButton.setBackground(getDrawable(R.drawable.ic_directions_walk_white_24dp));
        }
    }

    public void detectMotion(){
//        Log.d("motion detection","on");

        if(motionDetectorState == 0){
            nativeScreenShot(Environment.getExternalStorageDirectory()+File.separator + "image0.png");
            motionDetectorState += 1;

        }
        else if(motionDetectorState == 1){
            nativeScreenShot(Environment.getExternalStorageDirectory()+File.separator + "image1.png");
            motionDetectorState += 1;
        }
        else {
            motionDetectorState = 0;
            Bitmap image0 = BitmapFactory.decodeFile(
                    Environment.getExternalStorageDirectory()+File.separator + "image0.png");

            Bitmap image1 = BitmapFactory.decodeFile(
                    Environment.getExternalStorageDirectory()+File.separator + "image1.png");

//            Log.d("bitmaps", String.valueOf(image0.getPixel(5,5)&0xff) + "-----" + String.valueOf(image1.getHeight()));

            float p0 = 0;
            float p1 = 0;
            float difference = 0;

            int m0 = 0;
            int m1 = 0;

            for(int x=0; x<640; x+=10 ){
                for(int y=0; y<480; y+=10 ){
                    m0 =  image0.getPixel(x, y);
                    m1 =  image1.getPixel(x, y);

                    p0 = ((m0 >> 16)&0xff) + ((m0 >> 8)&0xff) + (m0&0xff);
                    p1 = ((m1 >> 16)&0xff) + ((m1 >> 8)&0xff) + (m1&0xff);

                    p0 /=3;
                    p1 /=3;

                    difference += Math.abs(p0-p1);

                }
            }
//            Log.d("difference",String.valueOf(difference));

            if (difference > motionThreshold){
                Log.d("motion","detected");
                screenShot();
                motionStartTime = System.currentTimeMillis();
                showInfoDialog(getResources().getString(R.string.motion_detected));
            }

        }

    }

    public void startTimer() {
        //set a new Timer
        motionDetectionTimer = new Timer();

        //initialize the TimerTask's job
        initializeTimerTask();

        //schedule the timer, after the first 5000ms the TimerTask will run every 10000ms
        motionDetectionTimer.schedule(motionDetectionTimerTask, 10, 350); //
    }

    public void stopTimerTask() {
        //stop the timer, if it's not already null
        if (motionDetectionTimer != null) {
            motionDetectionTimer.cancel();
            motionDetectionTimer = null;
        }
    }

    public void initializeTimerTask() {

        motionDetectionTimerTask = new TimerTask() {
            public void run() {

                //use a handler to run a toast that shows the current timestamp
                motionDetectionTimerHandler.post(new Runnable() {
                    public void run() {
//                        Log.d(String.valueOf(System.currentTimeMillis()), String.valueOf(motionStartTime) + "  " +String.valueOf((System.currentTimeMillis() - motionStartTime)));
                        if((System.currentTimeMillis() - motionStartTime) > motionDuration)
                            detectMotion();
                    }
                });
            }
        };
    }

    public void startUdpTimer() {
        //set a new Timer
        udpTimer = new Timer();

        //initialize the TimerTask's job
        initializeUdpTimerTask();

        //schedule the timer, after the first 5000ms the TimerTask will run every 10000ms
        udpTimer.schedule(udpTimerTask, 1000, 250); //
    }

    public void stopUdpTimerTask() {
        //stop the timer, if it's not already null
        if (udpTimer != null) {
            udpTimer.cancel();
            udpTimer = null;
        }
    }

    public void initializeUdpTimerTask() {

        udpTimerTask = new TimerTask() {
            public void run() {

                //use a handler to run a toast that shows the current timestamp
                udpTimerHandler.post(new Runnable() {
                    public void run() {
                       //udpReceive();
                    }
                });
            }
        };
    }

    public void showInfoDialog(String msg){
        if(!infoDialog.isShowing()){
            infoDialog.show();
        }
        infoDialogText.setText(msg);
    }

    public void udpReceive(){
        DatagramPacket receivePacket = new DatagramPacket(receiveData, receiveData.length);
        try {
            receiveSocket.receive(receivePacket);

            Log.d("msg", Arrays.toString(receiveData));

            byte [] message = receivePacket.getData();

            int yaw = (message[0] & 0xff) << 8 | (message[1] & 0xff);
            if(vehicle.getDirection() != yaw){
                directionImage.setRotation(yaw);
                vehicle.setDirection(yaw);
            }

//            vehicle.setPositionUp(((message[6] & 0b00001000) >> 3)==0b00000001);
            if(isAutoFlipOn){
                if((((message[6]&0xff) & 0b00001000) >> 3)==0b00000001)
                    nativeVideoFlipTo2();
                else {
                    nativeVideoFlipTo0();
                }
            }

            int payloadId = ((message[6] &0xff) & (0b00110000 )) >> 4;
            if (vehicle.getPayloadId() != payloadId)
                vehicle.setPayloadId(payloadId);

            vehicle.updateImuStatus(message[7] & 0xff);
            vehicle.updatePayloadStatus(message[8] & 0xff);

            int batteryInfo = message[9]&0xff;

            if (vehicle.getBatteryInfo() !=batteryInfo){
                batteryInfoText.setText("%"+String.valueOf(batteryInfo));
                batteryInfoImage.setProgress(batteryInfo);
                if(battery_warning_10 && batteryInfo<10){
                    battery_warning_10 = false;
                    showInfoDialog(getString(R.string.battery_10));
                }
                else if(battery_warning_20 && batteryInfo<20){
                    battery_warning_20 = false;
                    showInfoDialog(getString(R.string.battery_10));
                }
                else if(battery_warning_30 && batteryInfo<30){
                    battery_warning_30 = false;
                    showInfoDialog(getString(R.string.battery_10));
                }

                vehicle.setBatteryInfo(batteryInfo);
            }

            int armPosition = (message[10] & 0xff) << 8 | (message[11] & 0xff);
            if(vehicle.getArmPosition() != armPosition){
                armPositionImage.setRotation(armPosition);
                vehicle.setArmPosition(armPosition);
            }


            if (vehicle.getReturnHomeState() !=0 && (message[12]&0x01) == 0x01)
                vehicle.setReturnHomeState(0);

            vehicle.setLatitude(((message[13] & 0xff) << 24 | (message[14] & 0xff) << 16
                    | (message[15] & 0xff) << 8 | (message[16] & 0xff))/1000000);

            vehicle.setLongitude(((message[17] & 0xff) << 24 | (message[18] & 0xff) << 16
                    | (message[19] & 0xff) << 8 | (message[20] & 0xff))/1000000);

        } catch (IOException e) {
            e.printStackTrace();
        }

            // send datagram
            byte [] sendData = new byte[17];

            sendData[0] = (byte) ((int) (control1.getNormalizedX()*2.55));
            sendData[1] = (byte) ((int) (255 - control1.getNormalizedY()*2.55));
            sendData[2] = 0;

            sendData[3] |= (0b00000011 & driveSpeedSpinner.getSelectedItemPosition());
            sendData[3] |= (0b00001100 & (frontLedState << 2));
            sendData[3] |= (0b00110000 & (backLedState << 4));

            if(control2.getNormalizedY() < 20){
                sendData[3] |= 0b01000000; // kol ileri
            }
            else if(control2.getNormalizedY() > 80){
                sendData[3] |= 0b10000000; // kol geri
            }

            sendData[4] |= (0b00000011 & driveModeSpinner.getSelectedItemPosition());
            sendData[4] |= (0b00000100 & autoFixSpinner.getSelectedItemPosition()<<2);
            sendData[4] |= (0b01111000 & (vehicle.getImuState(imuSpinner.getSelectedItemPosition())<<3));

            if((sendData[4] & 0b01111000)==0)
                imuSpinner.setSelection(0);

            sendData[4] |= (0b10000000 & (cameraSpinner.getSelectedItemPosition() ==0 ?  0:0b10000000));

            if (isPayloadActive){
                sendData[5] |= vehicle.getPayloadState();
                if (sendData[5]==0)
                    isPayloadActive = false;
            }

            if(isReturnHome){
                sendData[6] |= 0b00000001;
                sendData[4] &= ~0b00000100;
            }

            sendData[15] |= (0b00000011 & cameraSpinner.getSelectedItemPosition());
            sendData[15] |= (0b00111100 & (wifiChannelSpinner.getSelectedItemPosition() << 2));
            sendData[15] |= (0b11000000 & (disconnectionPolicySpinner.getSelectedItemPosition() << 6));

            if (isDestructOn){
                sendData[16] |= 0b00000011;
            }

            if (isRefreshWifi){
                sendData[16] |=0b00001100;
                isRefreshWifi = false;
            }


            DatagramPacket sendPacket = new DatagramPacket(sendData,sendData.length, vehicleIp, 5001);

        try {
            sendSocket.send(sendPacket);
        } catch (IOException e) {
            e.printStackTrace();
        }


//            Log.d("js:x",String.valueOf(control1.getNormalizedX()));
//            Log.d("js:y",String.valueOf(control1.getNormalizedY()));













    }

}

// no need to .. , wonderful wonderful life