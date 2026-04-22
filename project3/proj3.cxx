
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
#include <vtkCamera.h>


int main(int argc, char *argv[])
{
   vtkDataSetReader *reader = vtkDataSetReader::New();
   reader->SetFileName("noise.vtk");
   reader->Update();
   
   vtkLookupTable *lut = vtkLookupTable::New();

   // T4
   lut->SetNumberOfColors(256); // use all hex vals
   // lut->SetSaturationRange(1.0, 1.0);
   lut->SetHueRange(1.1, 0.6); // blue to red
   // lut->SetValueRange(1.0, 1.0);
   lut->Build();

   // mapper (slice)
   vtkDataSetMapper *mapper = vtkDataSetMapper::New();
   mapper->SetInputData(reader->GetOutput());
   mapper->SetLookupTable(lut);
   mapper->SetScalarRange(reader->GetOutput()->GetScalarRange());
   
   // actor (slice)
   vtkActor *actor = vtkActor::New();
   actor->SetMapper(mapper);
   
   // slice
   vtkPlane *plane = vtkPlane::New();  // T3
   plane->SetOrigin(0, 0, 0);
   plane->SetNormal(0, 0, 1);

   vtkCutter *cutter = vtkCutter::New();
   cutter->SetCutFunction(plane);
   cutter->SetInputConnection(reader->GetOutputPort());
   mapper->SetInputConnection(cutter->GetOutputPort());
   
   // render (slice)
   vtkRenderer *ren = vtkRenderer::New();
   ren->SetViewport(0.0, 0.0, 0.5, 1.0); // left
   ren->AddActor(actor);


   // T5 & T6 (second render + mapper + actor)

   // mapper (contour)
   vtkDataSetMapper *mapper2 = vtkDataSetMapper::New();
   mapper2->SetInputData(reader->GetOutput());
   mapper2->SetLookupTable(lut);
   mapper2->SetScalarRange(reader->GetOutput()->GetScalarRange());

   // actor (contour)
   vtkActor *actor2 = vtkActor::New();
   actor2->SetMapper(mapper2);
   
   // contour
   vtkContourFilter *contour = vtkContourFilter::New(); //T2
   contour->SetInputConnection(reader->GetOutputPort());
   // contour->SetValue(0, 2.4);
   // contour->SetValue(1, 4.0);
   mapper2->SetInputConnection(contour->GetOutputPort());

   // render (contour)
   vtkRenderer *ren2 = vtkRenderer::New();
   ren2->SetViewport(0.5, 0.0, 1.0, 1.0); // right
   ren2->AddActor(actor2);


   vtkRenderWindow *renwin = vtkRenderWindow::New();
   renwin->AddRenderer(ren);
   renwin->AddRenderer(ren2);


   vtkRenderWindowInteractor *iren = vtkRenderWindowInteractor::New();
   iren->SetRenderWindow(renwin);
   renwin->SetSize(768, 768); // T1
   renwin->Render();

   // T7
   while(1)
   {
      for (float i = 1.0; i < 6.2; i+= 0.02)
      {
         contour->SetValue(0, i);
         contour->Update();
         ren2->GetActiveCamera()->ShallowCopy(ren->GetActiveCamera());
         renwin->Render();
      }
   }

   iren->Start();

   // cleanup (reverse order of creation)
   
   iren->Delete();
   renwin->Delete();
   ren2->Delete();
   contour->Delete();
   actor2->Delete();
   mapper2->Delete();
   ren->Delete();
   cutter->Delete();
   plane->Delete();
   actor->Delete();
   mapper->Delete();
   lut->Delete();
   reader->Delete();
   
}


