package org.freedesktop.gstreamer.tutorials.tutorial_5;

import android.annotation.SuppressLint;
import android.content.Context;
import android.support.annotation.Nullable;
import android.util.AttributeSet;
import android.util.Log;
import android.view.MotionEvent;
import android.view.ScaleGestureDetector;
import android.view.SurfaceView;
import android.view.TextureView;
import android.view.View;
import android.view.ViewTreeObserver;
import android.widget.FrameLayout;
import android.widget.LinearLayout;

import org.freedesktop.gstreamer.GStreamer;
import org.freedesktop.gstreamer.tutorials.tutorial_5.ZoomableSurfaceView;
// https://github.com/m-damavandi/ZoomableSurfaceView/tree/master/app/src/main/java/com/damavandi
// A simple SurfaceView whose width and height can be set from the outside
public class GStreamerSurfaceView extends SurfaceView {
    public int media_width = 320;
    public int media_height = 240;

    private ScaleGestureDetector SGD;
    private Context context;
    private boolean isSingleTouch;
    private float width, height = 0;
    private float scale = 1f;
    private float minScale = 1f;
    private float maxScale = 10f;
    int left, top, right, bottom;

    private long touchStart = 0;
    private long touchDuration = 0;

    // Mandatory constructors, they do not do much
    public GStreamerSurfaceView(Context context, AttributeSet attrs,
            int defStyle) {
        super(context, attrs, defStyle);
        this.context = context;
        init();
    }

    public GStreamerSurfaceView(Context context, AttributeSet attrs) {
        super(context, attrs);
        this.context = context;
        init();
    }

    public GStreamerSurfaceView (Context context) {
        super(context);
        this.context = context;
        init();
    }


    // Called by the layout manager to find out our size and give us some rules.
    // We will try to maximize our size, and preserve the media's aspect ratio if
    // we are given the freedom to do so.
    @Override
    protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {
        int width = 0, height = 0;
        int wmode = View.MeasureSpec.getMode(widthMeasureSpec);
        int hmode = View.MeasureSpec.getMode(heightMeasureSpec);
        int wsize = View.MeasureSpec.getSize(widthMeasureSpec);
        int hsize = View.MeasureSpec.getSize(heightMeasureSpec);

        Log.i ("GStreamer", "onMeasure called with " + media_width + "x" + media_height);
        // Obey width rules
        switch (wmode) {
        case View.MeasureSpec.AT_MOST:
            if (hmode == View.MeasureSpec.EXACTLY) {
                width = Math.min(hsize * media_width / media_height, wsize);
                break;
            }
        case View.MeasureSpec.EXACTLY:
            width = wsize;
            break;
        case View.MeasureSpec.UNSPECIFIED:
            width = media_width;
        }

        // Obey height rules
        switch (hmode) {
        case View.MeasureSpec.AT_MOST:
            if (wmode == View.MeasureSpec.EXACTLY) {
                height = Math.min(wsize * media_height / media_width, hsize);
                break;
            }
        case View.MeasureSpec.EXACTLY:
            height = hsize;
            break;
        case View.MeasureSpec.UNSPECIFIED:
            height = media_height;
        }

        // Finally, calculate best size when both axis are free
        if (hmode == View.MeasureSpec.AT_MOST && wmode == View.MeasureSpec.AT_MOST) {
            int correct_height = width * media_height / media_width;
            int correct_width = height * media_width / media_height;

            if (correct_height < height)
                height = correct_height;
            else
                width = correct_width;
        }

        // Obey minimum size
        width = Math.max (getSuggestedMinimumWidth(), width);
        height = Math.max (getSuggestedMinimumHeight(), height);
        setMeasuredDimension(width, height);
    }

    private void init() {
        setOnTouchListener(new GStreamerSurfaceView.MyTouchListeners());
        SGD = new ScaleGestureDetector(context, new GStreamerSurfaceView.ScaleListener());
//        this.getViewTreeObserver().addOnGlobalLayoutListener(new ViewTreeObserver.OnGlobalLayoutListener() {
//            @Override
//            public void onGlobalLayout() {
//
//            }
//        });

//        GStreamerSurfaceView.this.setOnLongClickListener(new OnLongClickListener() {
//            @Override
//            public boolean onLongClick(View view) {
//
//                Log.d("here","*********************************************");
//                scale = 1f;
//                GStreamerSurfaceView.this.setScaleX(scale);
//                GStreamerSurfaceView.this.setScaleY(scale);
//                return true;
//            }
//        });


        
    }

    @Override
    protected void onLayout(boolean changed, int left, int top, int right, int bottom) {
        super.onLayout(changed, left, top, right, bottom);
        if (width == 0 && height == 0) {
            width = GStreamerSurfaceView.this.getWidth();
            height = GStreamerSurfaceView.this.getHeight();
            this.left = left;
            this.right = right;
            this.top = top;
            this.bottom = bottom;
        }

    }

    private class MyTouchListeners implements View.OnTouchListener {

        float dX, dY;

        MyTouchListeners() {
            super();
        }

        @SuppressLint("ClickableViewAccessibility")
        @Override
        public boolean onTouch(View view, MotionEvent event) {
//            Log.d("motion event",event.toString());


            SGD.onTouchEvent(event);
            if (event.getPointerCount() > 1) {
                isSingleTouch = false;
            } else {
                if (event.getAction() == MotionEvent.ACTION_UP) {
                    isSingleTouch = true;
                }
            }
            switch (event.getAction()) {
                case MotionEvent.ACTION_UP:
                    if (isSingleTouch && (System.currentTimeMillis() - touchStart)>3000){
                        scale = 1f;
                        GStreamerSurfaceView.this.setScaleX(scale);
                        GStreamerSurfaceView.this.setScaleY(scale);
                    }
                    break;

                case MotionEvent.ACTION_DOWN:
                    dX = GStreamerSurfaceView.this.getX() - event.getRawX();
                    dY = GStreamerSurfaceView.this.getY() - event.getRawY();

                    touchStart = System.currentTimeMillis();
                    break;

                case MotionEvent.ACTION_MOVE:
                    if (isSingleTouch) {
                        GStreamerSurfaceView.this.animate()
                                .x(event.getRawX() + dX)
                                .y(event.getRawY() + dY)
                                .setDuration(0)
                                .start();
                        checkDimension(GStreamerSurfaceView.this);
                    }
                    break;
                default:
                    return true;
            }
            return true;
        }
    }

    private class ScaleListener extends ScaleGestureDetector.SimpleOnScaleGestureListener {

        @Override
        public boolean onScale(ScaleGestureDetector detector) {
            detector.setQuickScaleEnabled(true);
//            detector.setStylusScaleEnabled(true);
            scale *= detector.getScaleFactor();
            scale = Math.max(minScale, Math.min(scale, maxScale));
//            Log.d("onGlobalLayout: ", scale + "************************************ " + width + " " + height);


            GStreamerSurfaceView.this.setPivotX(detector.getFocusX());
            GStreamerSurfaceView.this.setPivotY(detector.getFocusY());
            GStreamerSurfaceView.this.setScaleX(scale);
            GStreamerSurfaceView.this.setScaleY(scale);

//            GStreamerSurfaceView.this.setScaleY(height*scale);


//            FrameLayout.LayoutParams params = new FrameLayout.LayoutParams(
//                    (int) (width * scale), (int) (height * scale));
//            GStreamerSurfaceView.this.setLayoutParams(params);
//            checkDimension(GStreamerSurfaceView.this);
            return true;
        }
    }


    private void checkDimension(View vi) {
        if (vi.getX() > left) {
            vi.animate()
                    .x(left)
                    .y(vi.getY())
                    .setDuration(0)
                    .start();
        }

        if ((vi.getWidth() + vi.getX()) < right) {
            vi.animate()
                    .x(right - vi.getWidth())
                    .y(vi.getY())
                    .setDuration(0)
                    .start();
        }

        if (vi.getY() > top) {
            vi.animate()
                    .x(vi.getX())
                    .y(top)
                    .setDuration(0)
                    .start();
        }

        if ((vi.getHeight() + vi.getY()) < bottom) {
            vi.animate()
                    .x(vi.getX())
                    .y(bottom - vi.getHeight())
                    .setDuration(0)
                    .start();
        }
    }
}
