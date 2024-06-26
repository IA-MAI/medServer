
import os, sys, time
import SimpleITK as sitk

def resample_image(input_image, new_size=(256, 256, 256), interpolator=sitk.sitkLinear):
    original_spacing = input_image.GetSpacing()
    original_size = input_image.GetSize()

    new_spacing = [
        (original_size[0] * original_spacing[0]) / new_size[0],
        (original_size[1] * original_spacing[1]) / new_size[1],
        (original_size[2] * original_spacing[2]) / new_size[2]
    ]

    resample = sitk.ResampleImageFilter()
    resample.SetInterpolator(interpolator)
    resample.SetOutputDirection(input_image.GetDirection())
    resample.SetOutputOrigin(input_image.GetOrigin())
    resample.SetOutputSpacing(new_spacing)
    resample.SetSize(new_size)

    return resample.Execute(input_image)

def main(inputPath,outputPath, processID):
    if processID =="0":
       print("processID: 0")
    #    for i in range(6):
    #        time.sleep(10)
    #        print("processing.....!")
       os.system("cp " + inputPath + " " + outputPath )
    elif processID =="1":
        print("processID: 1")
        new_size=(256, 256, 256)
        interpolator=sitk.sitkLinear        
        print(f"Resampling image to ", new_size)
        input_image = sitk.ReadImage(inputPath)
        resampled_image = resample_image(input_image,new_size=new_size, interpolator=interpolator)
        sitk.WriteImage(resampled_image, outputPath)

if __name__ == '__main__':    
    print("process Data")
    # inputPath  = os.path.join(os.path.expanduser("~"),"myGit","tmpData","sub-stroke0003_ses-02_dwi.nii.gz")
    # outputPath = os.path.join(os.path.expanduser("~"),"myGit","tmpData","sub-stroke0003_ses-02_dwi_result.nii.gz")
    # processID = 0
    #main(inputPath,outputPath, processID)
    if len(sys.argv) >= 4:
        inputPath  = sys.argv[1]
        outputPath = sys.argv[2]
        processID  = sys.argv[3]
        main(inputPath,outputPath, processID)
    else:
        print("Usage: python proceeData.py <inputPath> <outputPath> <processID>")
