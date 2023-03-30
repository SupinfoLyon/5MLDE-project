import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { UntypedFormBuilder, UntypedFormGroup, Validators } from '@angular/forms';

type predictionInput = {
  [key: string]: "str" | "int";
}

@Component({
  selector: 'app-form',
  templateUrl: './form.component.html',
  styleUrls: ['./form.component.scss']
})
export class FormComponent {
  prediction: number | undefined;
  validateForm!: UntypedFormGroup;
  inputs: predictionInput = {}

  constructor(private fb: UntypedFormBuilder, private http: HttpClient) {

  }

  handlePrediction(data: {
    [key: string]: string | number;
  }){
    console.log(data)
    this.http.post("http://localhost:8000/predict", data, {
      headers: {
        'Content-Type': 'application/json',
      }
    }).subscribe((data:any) => {
      console.log(data)
      this.prediction = data.prediction[0]
    })
  }

  submitForm(): void {  
    console.log("submitForm", this.validateForm);
    
    if (this.validateForm.valid) {
      console.log('submit', this.validateForm.value);
      const data = this.validateForm.value as {
        [key: string]: string | number;
      }
      // for each key in data, replaceAll " " by "_"
      for (const [key, value] of Object.entries(data)) {
        data[key] = value.toString().replaceAll(" ", "_")
      }
      this.handlePrediction(this.validateForm.value)
    } else {
      Object.values(this.validateForm.controls).forEach(control => {
        if (control.invalid) {
          control.markAsDirty();
          control.updateValueAndValidity({ onlySelf: true });
        }
      });
    }
  }

  getInputs() {
    // call api with httpclient
    this.http.get("http://localhost:8000/params").subscribe((data: any) => {
      this.inputs = data as predictionInput
      console.log(this.inputs)

      // create form
      const form: {
        [key: string]: any;
      } = {}
      for (const [key, value] of Object.entries(this.inputs)) {
        form[key] = [null, [Validators.required]]
      }
      this.validateForm = this.fb.group(form);

    });
  }

  ngOnInit(): void {
    this.getInputs()
  }


}
