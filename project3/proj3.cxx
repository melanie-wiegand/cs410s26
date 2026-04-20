
#include <vtkRenderWindow.h>
#include <vtkRenderer.h>
#include <vtkRenderWindowInteractor.h>
#include <vtkDataSetReader.h>
#include <vtkDataSetMapper.h>
#include <vtkActor.h>
#include <vtkLookupTable.h>
#include <vtkContourFilter.h>
#include <vtkPlane.h>
#include <vtkCutter.h>


int main(int argc, char *argv[])
{
   vtkDataSetReader *reader = vtkDataSetReader::New();
   reader->SetFileName("noise.vtk");
   reader->Update();

   vtkDataSetMapper *mapper = vtkDataSetMapper::New();
   mapper->SetInputData(reader->GetOutput());
   
   vtkLookupTable *lut = vtkLookupTable::New();

   // T4
   
   lut->SetNumberOfColors(256); // use all hex vals
   
   // lut->SetSaturationRange(1.0, 1.0);
   lut->SetHueRange(1.1, 0.6); // blue to red
   // lut->SetValueRange(1.0, 1.0);
   lut->Build();

   mapper->SetLookupTable(lut);
   mapper->SetScalarRange(reader->GetOutput()->GetScalarRange());
   
   vtkActor *actor = vtkActor::New();
   actor->SetMapper(mapper);

   vtkRenderer *ren = vtkRenderer::New();
   ren->AddActor(actor);

   vtkRenderWindow *renwin = vtkRenderWindow::New();
   renwin->AddRenderer(ren);

   vtkContourFilter *contour = vtkContourFilter::New(); //T2
   contour->SetInputConnection(reader->GetOutputPort());
   contour->SetValue(0, 2.4);
   contour->SetValue(1, 4.0);
   mapper->SetInputConnection(contour->GetOutputPort());


   // vtkPlane *plane = vtkPlane::New();  // T3
   // plane->SetOrigin(0, 0, 0);
   // plane->SetNormal(0, 0, 1);

   // vtkCutter *cutter = vtkCutter::New();
   // cutter->SetCutFunction(plane);
   // cutter->SetInputConnection(reader->GetOutputPort());
   // mapper->SetInputConnection(cutter->GetOutputPort());


   vtkRenderWindowInteractor *iren = vtkRenderWindowInteractor::New();
   iren->SetRenderWindow(renwin);
   renwin->SetSize(768, 768); // T1
   renwin->Render();
   iren->Start();

   // cleanup
   // contour->Delete();
   iren->Delete();
   renwin->Delete();
   ren->Delete();
   actor->Delete();
   lut->Delete();
   mapper->Delete();
   reader->Delete();
}


